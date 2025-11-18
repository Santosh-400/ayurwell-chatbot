from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from utils.image_desc import describe_image
from workflow.graph import build_workflow
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import sys
import requests
import base64
import io
from dotenv import load_dotenv
from edge_tts_helper import text_to_speech_edge # Use Edge TTS

try:
    # Optional dependency: google genai SDK for Gemini translation
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

# Load .env automatically if present so GOOGLE_API_KEY and others are available to the app
load_dotenv()

# Ensure stdout/stderr use UTF-8 encoding on platforms (Windows) with legacy codepages
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    # best-effort — continue if not supported
    pass

app = Flask(__name__)
CORS(app)
# Compatibility shim: some versions of the google generative client don't accept
# a `max_retries` kwarg while the langchain-google-genai adapter may pass it.
# Patch GenerativeServiceClient.generate_content at runtime to silently drop
# unsupported kwargs (safe, minimal change to restore functionality).
try:
    from google.ai import generativelanguage
    if hasattr(generativelanguage, "GenerativeServiceClient"):
        orig = generativelanguage.GenerativeServiceClient.generate_content

        def _patched_generate_content(self, *args, **kwargs):
            if "max_retries" in kwargs:
                kwargs.pop("max_retries")
            return orig(self, *args, **kwargs)

        generativelanguage.GenerativeServiceClient.generate_content = _patched_generate_content
        app.logger.info("Patched GenerativeServiceClient.generate_content to ignore max_retries kwarg")
except Exception as _patch_e:
    # If the package isn't available or patching fails, continue; errors will be visible in logs
    app.logger.warning(f"Could not apply generative client patch: {_patch_e}")

try:
    chatbot = build_workflow()
    print("Workflow built successfully")
except Exception as e:
    print(f"Error building workflow: {e}")
    chatbot = None

# Setup image upload path
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("ui.html")


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    text_input = request.form.get("message", "").strip()
    lang = request.form.get("lang", "en").strip() or "en"
    image_file = request.files.get("image")
    
    final_query = ""

    # If image is provided
    if image_file:
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)

        image_result = describe_image(filepath)

        if "description" in image_result:
            final_query = image_result["description"]
        else:
            return jsonify({"reply": f"Image processing error: {image_result['error']}"})
    
    # If text is provided (use either or both)
    if text_input:
        final_query = f"{text_input}. " + final_query if final_query else text_input

    if not final_query:
        return jsonify({"reply": "Please provide a question or an image."})

    if chatbot is None:
        return jsonify({"reply": "Sorry, the chatbot is not properly initialized. Please check the configuration and try again later."})

    input_data = {"question": HumanMessage(content=final_query)}
    # If the incoming language is Kannada, translate it to English for retrieval
    translator = None
    translated_query = final_query
    try:
        app.logger.info(f"/chat received. lang={lang}, original_query={final_query[:200]}")
        # Prefer Google GenAI for translation if available
        if lang == 'kn':
            if genai is not None:
                try:
                    # use GenAI to translate Kannada -> English
                    client = genai.Client(api_key=os.getenv('GOOGLE_GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY'))
                    prompt = f"Translate the following Kannada text to English, return only the translated text:\n\n{final_query}"
                    resp = client.models.generate_content(model="text-bison-001", contents=prompt, config=types.GenerateContentConfig())
                    # attempt to extract textual content from response
                    translated_query = None
                    try:
                        cand = resp.candidates[0]
                        # candidate.content may be a list of content blocks
                        c0 = cand.content[0]
                        if hasattr(c0, 'text') and c0.text:
                            translated_query = c0.text
                        else:
                            # try parts
                            if hasattr(c0, 'parts') and c0.parts:
                                for p in c0.parts:
                                    if hasattr(p, 'text') and p.text:
                                        translated_query = p.text
                                        break
                    except Exception:
                        translated_query = None
                    if translated_query:
                        app.logger.info(f"Translated KN->EN via GenAI: {translated_query[:200]}")
                    else:
                        app.logger.warning("GenAI translation returned no text, falling back to original query")
                        translated_query = final_query
                except Exception as te:
                    app.logger.warning(f"GenAI KN->EN translation failed: {te}")
                    translated_query = final_query
            else:
                # Fallback to deep_translator (safer) then googletrans if available
                try:
                    from deep_translator import GoogleTranslator
                    translated_query = GoogleTranslator(source='auto', target='en').translate(final_query)
                    app.logger.info(f"Translated KN->EN via deep_translator: {translated_query[:200]}")
                except Exception as de:
                    app.logger.debug(f"deep_translator KN->EN failed: {de}")
                    try:
                        from googletrans import Translator
                        translator = Translator()
                        translated_query = translator.translate(final_query, dest='en').text
                        app.logger.info(f"Translated KN->EN via googletrans: {translated_query[:200]}")
                    except Exception as te:
                        app.logger.warning(f"Failed to translate KN->EN with googletrans: {te}")
                        translated_query = final_query

        # Call chatbot with the (possibly translated) query
        input_data = {"question": HumanMessage(content=translated_query)}
        result = chatbot.invoke(input=input_data, config={"configurable": {"thread_id": 3}})
    except Exception as e:
        # Log traceback and return a friendly fallback message
        import traceback
        app.logger.exception("Chatbot workflow failed")
        tb = traceback.format_exc()
        # Return the exception details to help debugging (temporary)
        return jsonify({
            "reply": "Sorry, I'm having trouble answering right now. Please try again later.",
            "error": str(e),
            "trace": tb,
        })

    # Safely extract reply
    try:
        reply = result["messages"][-1].content if "messages" in result and result["messages"] else "Sorry, I'm unable to generate a response right now."
    except Exception:
        reply = "Sorry, I'm unable to generate a response right now."

    app.logger.info(f"Chatbot reply (pre-translate): {reply[:200]}")

    # If original request was Kannada, translate the reply back to Kannada before returning
    if lang == 'kn':
        # Prefer GenAI for translation back to Kannada
        if genai is not None:
            try:
                client = genai.Client(api_key=os.getenv('GOOGLE_GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY'))
                prompt = f"Translate the following English text to Kannada. Return only the translated Kannada text:\n\n{reply}"
                resp = client.models.generate_content(model="text-bison-001", contents=prompt, config=types.GenerateContentConfig())
                translated_reply = None
                try:
                    cand = resp.candidates[0]
                    c0 = cand.content[0]
                    if hasattr(c0, 'text') and c0.text:
                        translated_reply = c0.text
                    else:
                        if hasattr(c0, 'parts') and c0.parts:
                            for p in c0.parts:
                                if hasattr(p, 'text') and p.text:
                                    translated_reply = p.text
                                    break
                except Exception:
                    translated_reply = None
                if translated_reply:
                    app.logger.info(f"Translated EN->KN via GenAI: {translated_reply[:200]}")
                    reply = translated_reply
                else:
                    app.logger.warning("GenAI EN->KN translation returned no text; keeping English reply")
            except Exception as te:
                app.logger.warning(f"GenAI EN->KN translation failed: {te}")
                # fallback to deep_translator then googletrans
                try:
                    from deep_translator import GoogleTranslator
                    translated_reply = GoogleTranslator(source='auto', target='kn').translate(reply)
                    reply = translated_reply
                    app.logger.info(f"Translated EN->KN via deep_translator: {translated_reply[:200]}")
                except Exception as de:
                    app.logger.debug(f"deep_translator EN->KN failed: {de}")
                    try:
                        from googletrans import Translator
                        translator = Translator()
                        translated_reply = translator.translate(reply, dest='kn').text
                        reply = translated_reply
                        app.logger.info(f"Translated EN->KN via googletrans: {translated_reply[:200]}")
                    except Exception as e:
                        app.logger.warning(f"googletrans EN->KN failed: {e}")
        else:
            # genai not available: use deep_translator then googletrans if possible
            try:
                from deep_translator import GoogleTranslator
                translated_reply = GoogleTranslator(source='auto', target='kn').translate(reply)
                reply = translated_reply
                app.logger.info(f"Translated EN->KN via deep_translator: {translated_reply[:200]}")
            except Exception as de:
                app.logger.debug(f"deep_translator EN->KN failed: {de}")
                try:
                    from googletrans import Translator
                    translator = Translator()
                    translated_reply = translator.translate(reply, dest='kn').text
                    reply = translated_reply
                    app.logger.info(f"Translated EN->KN via googletrans: {translated_reply[:200]}")
                except Exception as e:
                    app.logger.warning(f"googletrans EN->KN failed: {e}")

    return jsonify({"reply": reply})


@app.route('/tts', methods=['POST'])
def tts_edge():
    """
    Unified TTS endpoint using gTTS for English and Edge TTS for Kannada.
    Accepts JSON: {"text": "...", "lang": "en|kn"}
    Returns audio/mpeg MP3 bytes.
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('message')
    lang = (payload.get('lang') or 'en').strip().lower()

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # Define voices using Edge TTS for both languages
    if lang == 'kn':
        voice = "kn-IN-SapnaNeural"  # Kannada Female
    else:
        voice = "en-IN-NeerjaNeural"   # Indian English Female (clear voice)

    app.logger.info(f"Generating TTS for lang='{lang}' with voice='{voice}'")

    try:
        # Use Edge TTS for both English and Kannada
        audio_bytes = text_to_speech_edge(text, voice)
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=f'speech_{lang}.mp3'
        )
    except Exception as e:
        app.logger.exception('Edge TTS generation failed')
        return jsonify({'error': 'Edge TTS generation failed', 'details': str(e)}), 500




# All old TTS endpoints have been removed and replaced by the new /tts endpoint above.

if __name__ == "__main__":
    # Get port from environment variable (for cloud deployment) or default to 8080
    # Changed from 5000 to 8080 to avoid conflicts with other services
    port = int(os.environ.get("PORT", 8182))
    # Disable debug mode in production (cloud environments)
    debug_mode = os.environ.get("FLASK_ENV", "production") == "development"
    # use_reloader=False prevents "signal only works in main thread" error in cloud deployments
    app.run(debug=debug_mode, host="0.0.0.0", port=port, use_reloader=False)




@app.route('/tts_local', methods=['POST'])
def tts_local():
    """Local server-side TTS using gTTS for multilingual output (MP3).
    Accepts JSON: {"text": "...", "lang": "en"}
    Returns audio/mpeg MP3 bytes.
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('message')
    lang = (payload.get('lang') or 'en').strip()
    if not text:
        return jsonify({'error': 'No text provided.'}), 400
    # Allow explicit override of backend via env var PREFERRED_TTS: 'gemini'|'google'|'gtts'
    preferred = (os.getenv('PREFERRED_TTS') or '').strip().lower()

    # Optional tuning parameters for gTTS post-processing
    phase = (payload.get('phase') or payload.get('pace') or 'medium').strip().lower()
    humanize = bool(payload.get('humanize', True))

    # Helper: decide whether to try Gemini
    def _can_use_gemini():
        return genai is not None and types is not None and (os.getenv('GOOGLE_GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY'))

    try:
        # 1) If user explicitly requested gTTS, skip cloud providers
        if preferred == 'gtts':
            app.logger.info('PREFERRED_TTS=gtts — using gTTS fallback')
        else:
            # 2) If preferred is 'gemini', try Gemini first (may fail if no credentials)
            if preferred == 'gemini' and _can_use_gemini():
                app.logger.info('PREFERRED_TTS=gemini — using Gemini TTS')
                return tts_gemini()

            # 3) If Gemini is available (and not explicitly disabled), use it
            if preferred != 'gtts' and _can_use_gemini():
                app.logger.info('Using Gemini TTS (genai) for high-quality speech')
                return tts_gemini()

            # 4) If user explicitly requested Google Cloud TTS, try it
            if preferred == 'google' and os.getenv('GOOGLE_API_KEY'):
                app.logger.info('PREFERRED_TTS=google — using Google Cloud TTS')
                return tts()

            # 5) Next preference: Google Cloud Text-to-Speech via REST (requires GOOGLE_API_KEY)
            if preferred != 'gtts' and os.getenv('GOOGLE_API_KEY'):
                app.logger.info('Using Google Cloud Text-to-Speech for speech')
                return tts()

            # 5.5) Next, try a free, open-source alternative via a public LibreTranslate instance
            if preferred not in ['gtts', 'google', 'gemini']:
                app.logger.info('Attempting free TTS via public LibreTranslate instance.')
                try:
                    # This public instance might be unstable.
                    lt_tts_url = 'https://lt.vern.cc/api/v1/tts'
                    # The API expects 'voice' in 'lang_code#speaker_id' format.
                    voice_id = 'kn#upen' if lang == 'kn' else 'en#ljspeech'
                    
                    lt_resp = requests.post(
                        lt_tts_url,
                        json={'text': text, 'voice': voice_id},
                        timeout=25,
                        stream=True
                    )

                    if lt_resp.status_code == 200:
                        app.logger.info(f'Successfully streaming audio from LibreTranslate TTS with voice {voice_id}.')
                        # Stream the response directly to the client.
                        return send_file(io.BytesIO(lt_resp.content), mimetype='audio/wav', as_attachment=False, download_name=f'speech_{lang}.wav')
                    else:
                        app.logger.warning(f'LibreTranslate TTS failed with status {lt_resp.status_code}. Falling back.')
                except Exception as lt_e:
                    app.logger.warning(f'LibreTranslate TTS request failed: {lt_e}. Falling back.')

        # 6) Fallback: gTTS (uses Google Translate TTS endpoints) — works for Kannada and English
        app.logger.info('Falling back to gTTS for speech synthesis.')
        try:
            text_gtt = importlib.import_module('text_gtt')
        except Exception as e:
            app.logger.exception('Could not import text_gtt module')
            return jsonify({'error': 'Server misconfiguration: text_gtt module not found', 'details': str(e)}), 500

        try:
            mp3_bytes = text_gtt.text_to_speech_gtts(text, lang=lang, humanize=humanize, phase=phase)
            return send_file(io.BytesIO(mp3_bytes), mimetype='audio/mpeg', as_attachment=False, download_name=f'speech_{lang}.mp3')
        except Exception as e:
            app.logger.exception('gTTS generation failed in tts_local')
            return jsonify({'error': 'gTTS generation failed', 'details': str(e)}), 500
    except Exception as e:
        app.logger.exception('tts_local routing failed')
        return jsonify({'error': 'tts_local routing failed', 'details': str(e)}), 500


@app.route('/tts_gtts', methods=['POST'])
def tts_gtts():
    """Generate MP3 using gTTS. Accepts JSON: {"text": "...", "lang": "en"}
    Returns audio/mpeg binary on success.
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('message')
    lang = (payload.get('lang') or 'en').strip()
    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # Try importing the helper module `text_gtt` from the repo
    try:
        text_gtt = importlib.import_module('text_gtt')
    except Exception as e:
        app.logger.exception('Could not import text_gtt module')
        return jsonify({'error': 'Server misconfiguration: text_gtt module not found', 'details': str(e)}), 500

    try:
        mp3_bytes = text_gtt.text_to_speech_gtts(text, lang=lang)
        return send_file(io.BytesIO(mp3_bytes), mimetype='audio/mpeg', as_attachment=False, download_name=f'speech_{lang}.mp3')
    except Exception as e:
        app.logger.exception('gTTS generation failed')
        return jsonify({'error': 'gTTS generation failed', 'details': str(e)}), 500


@app.route('/tts_gemini', methods=['POST'])
def tts_gemini():
    """Generate speech using Google Gemini TTS (generative models).
    Expects JSON: {"text": "...", "voice": "Kore" (optional)}
    Requires env var GOOGLE_GENAI_API_KEY or GOOGLE_API_KEY to be set for the server.
    Returns: audio/wav bytes on success.
    """
    if genai is None or types is None:
        return jsonify({'error': 'google-genai SDK not installed on server.'}), 500

    api_key = os.getenv('GOOGLE_GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return jsonify({'error': 'Google GenAI API key not configured on server.'}), 400

    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('message')
    voice_name = payload.get('voice') or payload.get('voice_name') or 'Kore'
    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    try:
        # Initialize client with explicit api_key so it doesn't rely on application-default creds
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )

        # The SDK stores the audio bytes in the candidate content parts inline_data
        candidate = None
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
        if not candidate:
            return jsonify({'error': 'No audio candidate returned.'}), 502

        # Drill into the content parts for inline_data
        try:
            part = candidate.content.parts[0]
            data = part.inline_data.data
        except Exception:
            # Fallback: try to read .content[0] or similar shapes
            data = None

        if data is None:
            return jsonify({'error': 'No inline audio data found in provider response.'}), 502

        # If the SDK returns a base64 string, decode it; if bytes, use directly
        audio_bytes = None
        if isinstance(data, (bytes, bytearray)):
            audio_bytes = bytes(data)
        else:
            # assume base64-encoded string
            try:
                import base64 as _base64
                audio_bytes = _base64.b64decode(data)
            except Exception:
                # as last resort, try to convert str->bytes
                try:
                    audio_bytes = str(data).encode('utf-8')
                except Exception:
                    return jsonify({'error': 'Could not decode audio data'}), 502

        return send_file(io.BytesIO(audio_bytes), mimetype='audio/wav', as_attachment=False, download_name='speech.wav')
    except Exception as e:
        app.logger.exception('Gemini TTS request failed')
        return jsonify({'error': 'Gemini TTS request failed', 'details': str(e)}), 500


@app.route('/tts_capabilities', methods=['GET'])
def tts_capabilities():
    """Return which TTS backends are available on the server.
    Useful for the UI to decide whether to prefer Gemini TTS.
    """
    has_gemini = False
    try:
        api_key = os.getenv('GOOGLE_GENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if genai is not None and api_key:
            has_gemini = True
    except Exception:
        has_gemini = False
    return jsonify({'gemini': has_gemini})


@app.route('/tts_check', methods=['GET'])
def tts_check():
    """Quick pyttsx3 health-check endpoint.
    GET /tts_check?text=optional+text
    Returns JSON with available voices and a base64-encoded short WAV sample synthesized locally.
    Useful to verify the server can init pyttsx3 and produce audio without using the UI.
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices') or []
        voices_info = []
        for v in voices:
            try:
                voices_info.append({
                    'id': getattr(v, 'id', None),
                    'name': getattr(v, 'name', ''),
                    'languages': getattr(v, 'languages', [])
                })
            except Exception:
                voices_info.append({'id': None, 'name': str(v), 'languages': []})

        sample_text = request.args.get('text') or 'This is a local pyttsx3 test.'
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()
        engine.save_to_file(sample_text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, 'rb') as f:
            audio_bytes = f.read()
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        audio_b64 = base64.b64encode(audio_bytes).decode('ascii')
        return jsonify({'ok': True, 'voices': voices_info, 'sample_base64': audio_b64})
    except Exception as e:
        app.logger.exception('pyttsx3 test failed')
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/translate', methods=['POST'])
def translate():
    """Simple server-side proxy to LibreTranslate for client-side translation.
    Expects JSON: {"text": "...", "target": "kn"}
    Returns: {"translatedText": "..."}
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text')
    target = payload.get('target', 'kn')
    if not text:
        return jsonify({'error': 'No text provided.'}), 400
    # LibreTranslate public instance (rate-limited). If you have another translator, replace this.
    try:
        lt_url = 'https://libretranslate.de/translate'
        body = {'q': text, 'source': 'en', 'target': target, 'format': 'text'}
        r = requests.post(lt_url, data=body, timeout=15)
        if r.status_code != 200:
            app.logger.error(f'LibreTranslate failed: {r.status_code} {r.text}')
            return jsonify({'error': 'Translation provider error', 'details': r.text}), 502
        j = r.json()
        translated = j.get('translatedText') or j.get('result') or ''
        return jsonify({'translatedText': translated})
    except Exception as e:
        app.logger.exception('Translation failed')
        return jsonify({'error': 'Translation failed', 'details': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
