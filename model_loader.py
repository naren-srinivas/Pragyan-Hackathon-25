import google.generativeai as genai
from google.api_core import retry
from google.api_core.exceptions import GoogleAPIError

class ConstructionModel:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    @retry.Retry(exceptions=GoogleAPIError)  # Retry on API errors
    def generate_insights(self, prompt):
        try:
            response = self.model.generate_content(
                prompt,
                tools=[{"google_search_retrieval": {}}],
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 2000
                },
                safety_settings={
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
                }
            )
            return response.text if response.text else ""
        except GoogleAPIError as e:
            print(f"API Error: {str(e)}")
            return ""
        
        #tools=[{"google_search_retrieval": {}}],