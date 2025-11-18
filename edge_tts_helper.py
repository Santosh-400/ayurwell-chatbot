import asyncio
import io
from edge_tts import Communicate

async def _text_to_speech_edge_async(text: str, voice: str) -> bytes:
    """
    Asynchronously generates speech from text using edge-tts and returns MP3 bytes.
    """
    communicate = Communicate(text, voice)
    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])
    buffer.seek(0)
    return buffer.read()

def text_to_speech_edge(text: str, voice: str) -> bytes:
    """
    Synchronous wrapper for generating speech with edge-tts.
    This handles the asyncio event loop to make it callable from a synchronous context like Flask.
    """
    # Get or create a new event loop for the current thread
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'get_running_loop' fails in a new thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the async function and return the result
    return loop.run_until_complete(_text_to_speech_edge_async(text, voice))

if __name__ == '__main__':
    # A simple test to verify the helper works.
    # This will generate test files in the root directory.
    KANNADA_TEXT = "ನಮಸ್ಕಾರ, ಇದು ಮೈಕ್ರೋಸಾಫ್ಟ್ ಎಡ್ಜ್ ಟಿಟಿಎಸ್ ಪರೀಕ್ಷೆ."
    KANNADA_VOICE_FEMALE = "kn-IN-SapnaNeural"
    KANNADA_VOICE_MALE = "kn-IN-GaganNeural"
    ENGLISH_TEXT = "Hello, this is a test of the Microsoft Edge TTS."
    ENGLISH_VOICE = "en-US-AriaNeural"

    print(f"Generating Kannada speech (Female) with voice: {KANNADA_VOICE_FEMALE}...")
    try:
        kannada_audio = text_to_speech_edge(KANNADA_TEXT, KANNADA_VOICE_FEMALE)
        with open("edge_kannada_female_test.mp3", "wb") as f:
            f.write(kannada_audio)
        print("✅ Successfully saved 'edge_kannada_female_test.mp3'")
    except Exception as e:
        print(f"❌ Failed to generate Kannada speech: {e}")

    print(f"Generating Kannada speech (Male) with voice: {KANNADA_VOICE_MALE}...")
    try:
        kannada_audio = text_to_speech_edge(KANNADA_TEXT, KANNADA_VOICE_MALE)
        with open("edge_kannada_male_test.mp3", "wb") as f:
            f.write(kannada_audio)
        print("✅ Successfully saved 'edge_kannada_male_test.mp3'")
    except Exception as e:
        print(f"❌ Failed to generate Kannada speech: {e}")

    print(f"\nGenerating English speech with voice: {ENGLISH_VOICE}...")
    try:
        english_audio = text_to_speech_edge(ENGLISH_TEXT, ENGLISH_VOICE)
        with open("edge_english_test.mp3", "wb") as f:
            f.write(english_audio)
        print("✅ Successfully saved 'edge_english_test.mp3'")
    except Exception as e:
        print(f"❌ Failed to generate English speech: {e}")
