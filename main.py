import os
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from engine import extract_academic_event, MY_TIMEZONE, ACADEMIC_KEYWORDS

def run_sync_for_user(token_dict):
    # Build credentials from the OAuth session token
    creds = Credentials(
        token=token_dict['access_token'],
        refresh_token=token_dict.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"]
    )

    gmail = build('gmail', 'v1', credentials=creds)
    calendar = build('calendar', 'v3', credentials=creds)

    # Scan last 7 days to ensure no events are missed
    query = f"newer_than:7d ({' OR '.join(ACADEMIC_KEYWORDS)})"
    results = gmail.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    synced_events = []

    for msg in messages:
        m = gmail.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = m.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        snippet = m.get('snippet', "")

        # Process Subject | Snippet through the engine
        event = extract_academic_event(f"{subject} | {snippet}")
        
        if event:
            # Duplicate check: Is there already an event with this title today?
            time_min = event['start'].replace(hour=0, minute=0).isoformat() + 'Z'
            time_max = event['start'].replace(hour=23, minute=59).isoformat() + 'Z'
            
            existing = calendar.events().list(
                calendarId='primary', q=event['summary'], 
                timeMin=time_min, timeMax=time_max
            ).execute()

            if not existing.get('items', []):
                cal_body = {
                    'summary': event['summary'],
                    'description': f"Sync Source: {event['description']}",
                    'start': {'dateTime': event['start'].isoformat(), 'timeZone': MY_TIMEZONE},
                    'end': {'dateTime': event['end'].isoformat(), 'timeZone': MY_TIMEZONE},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 60},
                            {'method': 'popup', 'minutes': 1440},
                        ],
                    },
                }
                calendar.events().insert(calendarId='primary', body=cal_body).execute()
                synced_events.append(event)
                
    return synced_events