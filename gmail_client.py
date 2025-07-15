import os
import base64
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """
    Initializes and returns a Gmail API service instance,
    handling authentication and token regeneration automatically.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}. Proceeding to re-authenticate.")
                creds = None
        if not creds:
            print("Authentication required. Please follow the browser instructions.")
            print("IMPORTANT: Ensure 'http://localhost:8080/' is an authorized redirect URI in your Google Cloud OAuth Client settings.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            except FileNotFoundError:
                print("Error: 'credentials.json' not found. Please ensure the file is in the correct directory.")
                return None
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        return None

def get_latest_email():
    """Fetches the latest email from the user's Gmail inbox."""
    service = get_gmail_service()
    if not service:
        return "Failed to initialize Gmail service. Please check your credentials and configuration."
        
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return "No new messages found."

        msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        payload = msg['payload']
        
        print("--- Full Email Payload ---")
        print(json.dumps(payload, indent=2))
        print("---------------------------")

        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                # Recursively handle nested parts
                if 'parts' in part:
                    for sub_part in part['parts']:
                        if sub_part.get('mimeType') == 'text/plain' and 'data' in sub_part.get('body', {}):
                            body += base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8')
                elif part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'data' in payload.get('body', {}):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        if not body:
            return msg.get('snippet', 'No content found.')

        print("--- Fetched Email Content (Processed) ---")
        print(body)
        print("-----------------------------------------")
        return body

    except HttpError as error:
        return f"An error occurred: {error}"

if __name__ == '__main__':
    print(get_latest_email())