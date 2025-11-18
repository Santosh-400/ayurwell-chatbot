import google.generativeai as genai
import base64

# 1️⃣ Set your API key
API_KEY = "AIzaSyC-IchJAEDSxdB3ssux7nOGnoOpEJaakew"

# 2️⃣ Configure Gemini
genai.configure(api_key=API_KEY)

# 3️⃣ Prepare text
text_to_speak = "Hello there! I am a chatbot powered by Google's Gemini model."

# 4️⃣ Create model
model = genai.GenerativeModel("gemini-1.5-pro")

# 5️⃣ Request speech output (audio/mp3)
response = model.generate_content(
    [text_to_speak],
    generation_config={
        "response_mime_type": "audio/mp3"
    },
)

# 6️⃣ Extract and save audio file
audio_data = base64.b64decode(response.candidates[0].content.parts[0].inline_data.data)

with open("output.mp3", "wb") as f:
    f.write(audio_data)

print("✅ Audio generated and saved as output.mp3!")
