import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from engine import extract_academic_event, MY_TIMEZONE, ACADEMIC_KEYWORDS
import datetime
import base64

def run_sync_for_user(token_dict):
    creds = Credentials(
        token=token_dict['access_token'],
        refresh_token=token_dict.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"]
    )

    gmail = build('gmail', 'v1', credentials=creds)
    calendar = build('calendar', 'v3', credentials=creds)

    query = f"newer_than:7d ({' OR '.join(ACADEMIC_KEYWORDS)})"
    results = gmail.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    synced_events = []
    if not messages:
        st.info("No relevant academic emails found in the last 7 days.")
        return []

    st.subheader("🕵️ Scanning Inbox...")

    for msg in messages:
        m = gmail.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = m.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        
        # Body Decoding
        full_body = ""
        payload = m.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        full_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            data = payload.get('body', {}).get('data')
            if data:
                full_body = base64.urlsafe_b64decode(data).decode('utf-8')

        # Combine and Process
        combined_text = f"{subject} | {full_body if full_body else m.get('snippet', '')}"
        event = extract_academic_event(combined_text)
        
        if event:
            # Duplicate check
            time_min = event['start'].replace(hour=0, minute=0, second=0).isoformat() + 'Z'
            time_max = event['start'].replace(hour=23, minute=59, second=59).isoformat() + 'Z'
            
            existing = calendar.events().list(
                calendarId='primary', q=event['summary'], 
                timeMin=time_min, timeMax=time_max
            ).execute()

            if not existing.get('items', []):
                cal_body = {
                    'summary': event['summary'],
                    'description': event['description'],
                    'start': {'dateTime': event['start'].isoformat(), 'timeZone': MY_TIMEZONE},
                    'end': {'dateTime': event['end'].isoformat(), 'timeZone': MY_TIMEZONE},
                }
                calendar.events().insert(calendarId='primary', body=cal_body).execute()
                synced_events.append(event)
                st.success(f"✅ Scheduled: {event['summary']} on {event['start'].strftime('%b %d at %I:%M %p')}")
            else:
                st.info(f"⏭️ Already in Calendar: {subject}")
        else:
            st.error(f"❌ Could not find date/time in: {subject}")
                
    return synced_events