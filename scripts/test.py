from gtts import gTTS

def text_to_speech_gtts(text, lang='kn'):
    # lang='en' for English, 'kn' for Kannada
    tts = gTTS(text=text, lang=lang, slow=False)
    file_path = f"tts_{lang}.mp3"
    tts.save(file_path)
    print(f"✅ Audio saved: {file_path}")
    return file_path

# Example:
text_to_speech_gtts("ನಮಸ್ಕಾರ! ಆಯುರ್ವೆಲ್ ಚಾಟ್‌ಬಾಟ್‌ಗೆ ಸುಸ್ವಾಗತ.", lang='kn')
text_to_speech_gtts("Hello! Welcome to AyurWell chatbot.", lang='en')
