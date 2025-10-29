import os
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import pickle


class EmailFetcher:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.CLIENT_SECRETS_FILE = "credentials.json"
        self.REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://smart-inbox-ai-a6el.onrender.com/oauth2callback')

    def get_authorization_url(self):
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_secrets_file(
            self.CLIENT_SECRETS_FILE,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url

    def handle_callback(self, code):
        """Handle OAuth callback and get credentials"""
        flow = Flow.from_client_secrets_file(
            self.CLIENT_SECRETS_FILE,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Serialize credentials for session storage
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    def fetch_recent_emails(self, credentials, hours=24):
        """Fetch emails from last N hours"""
        # Recreate credentials object
        creds = Credentials(
            token=credentials['token'],
            refresh_token=credentials['refresh_token'],
            token_uri=credentials['token_uri'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            scopes=credentials['scopes']
        )

        service = build('gmail', 'v1', credentials=creds)

        # Calculate time range
        after_date = datetime.now() - timedelta(hours=hours)
        query = f'after:{int(after_date.timestamp())}'

        emails = []
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()

            messages = results.get('messages', [])

            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                email_data = self._parse_email(msg)
                emails.append(email_data)

        except Exception as e:
            print(f"Error fetching emails: {e}")

        return emails

    def _parse_email(self, message):
        """Parse Gmail API message into readable format"""
        headers = message['payload']['headers']

        # Extract key information
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'snippet': message.get('snippet', ''),
            'timestamp': int(message['internalDate']) / 1000
        }

        # Parse headers
        for header in headers:
            name = header['name'].lower()
            if name == 'from':
                email_data['sender'] = header['value']
            elif name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'to':
                email_data['recipient'] = header['value']
            elif name == 'date':
                email_data['date'] = header['value']

        # Extract body
        email_data['body'] = self._get_email_body(message['payload'])

        return email_data

    def _get_email_body(self, payload):
        """Extract email body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')

        return body[:1000]  # Limit body length
