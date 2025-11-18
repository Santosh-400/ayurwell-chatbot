import google.generativeai as genai


genai.configure(api_key="AIzaSyBWdnqHyyq9FAat9eF8nZfCygPI8vIF1aw")

# list available models
for model in genai.list_models():
    print(model.name)
