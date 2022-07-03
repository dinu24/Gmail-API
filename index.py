from __future__ import print_function
import base64
import os
import mimetypes
from email.message import EmailMessage
import google.auth

from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']


sender = 'me'
reciever = '<RECIEVER_ID>'  # Change <> with reciever's emailID
subject = 'Test mail'
content = 'This is automated draft mail'
attachment = None  # Add attachments if any

# Message creator. Creates and returns the message with encryption.


def Messenger():
    message = EmailMessage()
    message.set_content(content)
    message['To'] = reciever
    message['From'] = sender
    message['Subject'] = subject
    if attachment != None:
        type_subtype, _ = mimetypes.guess_type(attachment)
        maintype, subtype = type_subtype.split('/')

        with open(attachment, 'rb') as fp:
            attachment_data = fp.read()
        message.add_attachment(attachment_data, maintype, subtype)
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'raw': encoded_message
    }
    return create_message


def Drafter(service, create_message=Messenger()):
    try:
        draft = service.users().drafts().create(userId="me",
                                                body=create_message).execute()
        print('Draft created')
    except HttpError as error:
        print(F'An error occurred: {error}')
        draft = None
    return draft


def ThreadSearch(service):
    try:
        threads = service.users().threads().list(
            userId='me').execute().get('threads', [])
        for thread in threads:
            tdata = service.users().threads().get(
                userId='me', id=thread['id']).execute()
            nmsgs = len(tdata['messages'])
            if nmsgs > 1:
                msg = tdata['messages'][0]['payload']
                subject = ''
                for header in msg['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                if subject:  # skip if no Subject line
                    print(F'- {subject}, {nmsgs}')
    except HttpError as error:
        print(F'An error occurred: {error}')


# Sends the message returned by Messenger()
def sendMessage(service, create_message=Messenger()):
    try:
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print('Message sent')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


def main():
    """Shows basic usage of the Gmail API.
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    Messenger()
    sendMessage(service)
    ThreadSearch(service)


if __name__ == '__main__':
    main()
