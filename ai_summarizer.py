import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_and_summarize_chargeback(text):
    """
    Extracts structured chargeback data and summarizes additional context from email text.
    Returns a JSON object with the extracted details and summary.
    """
    # Define the prompt in a more robust way to avoid syntax errors
    prompt_template = '''Please analyze the following email content. Extract the key-value pairs related to the chargeback into a JSON object under the key 'chargeback_details'.

If there is any additional text or context in the email apart from these structured details, please summarize it. Place this summary under the key 'contextual_summary'.

If no additional contextual data is found, the value for 'contextual_summary' should be 'No contextual data available'.

Return a single valid JSON object containing both 'chargeback_details' and 'contextual_summary'.

Email content:
'''
    prompt = prompt_template + text
    print("--- Text received by AI Summarizer ---")
    print(text)
    print("-------------------------------------")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent assistant that extracts structured data from emails and summarizes contextual information, providing the output in a clean JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )
        
        response_content = response.choices[0].message.content
        # Clean the response to ensure it's a valid JSON string
        clean_json_string = response_content.strip().lstrip('```json\n').rstrip('\n```')
        return json.loads(clean_json_string)

    except json.JSONDecodeError:
        return {"error": "Failed to decode the LLM response into JSON.", "raw_response": response_content}
    except Exception as e:
        return {"error": f"An error occurred during processing: {e}"}