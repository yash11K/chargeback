import json
from gmail_client import get_latest_email
from ai_summarizer import extract_and_summarize_chargeback

def main():
    """Fetches the latest email, extracts chargeback data, and prints it as a JSON object."""
    email_content = get_latest_email()

    if "An error occurred" in email_content or "Failed to initialize" in email_content:
        print(email_content)
        return

    if "No new messages found" in email_content:
        print(email_content)
        return

    # Process the email content to extract and summarize
    chargeback_data = extract_and_summarize_chargeback(email_content)

    print("\n--- Extracted Chargeback Data ---")
    print(json.dumps(chargeback_data, indent=2))

if __name__ == "__main__":
    main()