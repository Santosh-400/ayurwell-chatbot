import base64
import requests
import io
from PIL import Image
from dotenv import load_dotenv
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logger.warning("GROQ API KEY is not set - image description will not work")

def describe_image(image_path):
    """
    Takes an image file path and returns a 1–2 line description about the image
    focused on health-related topics, or a fallback response if not health-related.
    """
    if not GROQ_API_KEY:
        return {"error": "Image processing is not configured. GROQ_API_KEY is missing."}
    
    try:
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            encoded_image = base64.b64encode(image_content).decode("utf-8")

        # Check image validity
        try:
            img = Image.open(io.BytesIO(image_content))
            img.verify()
        except Exception as e:
            logger.error(f"Invalid image format: {str(e)}")
            return {"error": f"Invalid image format: {str(e)}"}

        # Vision prompt: keep response short and useful for chaining
        prompt_text = (
         "What does this image show? "
         "describe it in a 1-2 line query strictly including the main context.\n\n"
         "Examples:\n"
         "- If the image shows a person with a headache, respond: 'person has a problem with headache'.\n"
         "- If the image shows scalp issues, respond: 'person has a problem with scalp in the head'.\n"
         "- If the image shows medicine packaging, respond like: 'The medicine name is [medicine_name], and main description given on the package'."
         "-whatever its about describes just return in one line"
         "like this only give short description"
)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]

        # Make the request to Groq API
        response = requests.post(
            GROQ_API_URL,
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": messages,
                "max_tokens": 500
            },
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        description = data.get("choices", [{}])[0].get("message", {}).get("content", "No description found.")

        return {"description": description.strip()}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}

# Run and test the function
if __name__ == "__main__":
    image_path = "c.jpeg"  # Replace with your test image
    result = describe_image(image_path)

    if "error" in result:
        print("Error:", result["error"])
    else:
        query = result["description"]
        print("Image Description:", query)
        
        # Create the input data for invoking the system