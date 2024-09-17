import google.generativeai as genai
import json
from config import GOOGLE_AI_API_KEY

genai.configure(api_key=GOOGLE_AI_API_KEY)

def process_with_gemini(transcript: str) -> dict:
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')
        
        with open('src/prompts/meta_prompt.txt', 'r') as file:
            prompt = file.read()
        prompt += transcript
        
        response = model.generate_content(prompt)
        print(response.text)
        
        # Check for backticks at the beginning and end
        lines = response.text.splitlines()
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            # Remove first and last lines if they are backticks
            response_text = "\n".join(lines[1:-1])
        else:
            response_text = response.text
        
        try:
            # Attempt to parse the response as JSON
            json_response = json.loads(response_text)
            return json_response
        except json.JSONDecodeError:
            raise ValueError("Gemini response is not valid JSON.")
    
    except Exception as e:
        raise Exception(f"Error processing with Gemini: {str(e)}")