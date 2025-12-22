import re
import dateparser
import datetime

# Categories for maximum coverage
ACADEMIC_KEYWORDS = [
    "assignment", "exam", "submission", "project", "viva", "quiz", "test", 
    "deadline", "presentation", "workshop", "seminar", "session", "webinar", 
    "meetup", "hackathon", "lab", "tutorial", "lecture"
]

MY_TIMEZONE = 'Asia/Kolkata'

def extract_academic_event(text):
    # Split incoming text into Subject and Snippet
    parts = text.split(" | ", 1)
    email_subject = parts[0] if len(parts) > 0 else "Academic Event"
    clean_text = " ".join(text.split())
    
    keywords_regex = "|".join(ACADEMIC_KEYWORDS)
    # Detect Keyword followed by a date pattern
    pattern = rf"({keywords_regex}).*?(\d{{1,2}}(?:st|nd|rd|th)?\s+\w+|\d{{1,2}}[/-]\d{{1,2}})"
    
    match = re.search(pattern, clean_text, re.IGNORECASE)
    
    if match:
        event_label = match.group(1).capitalize()
        # Look for date context around the match
        context_window = clean_text[match.start():match.start()+150]
        
        parsed_date = dateparser.parse(context_window, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.datetime.now(),
            'REQUIRE_PARTS': ['day', 'month'],
            'TIMEZONE': MY_TIMEZONE,
            'RETURN_AS_TIMEZONE_AWARE': False
        })

        if parsed_date:
            # Set duration based on event type
            duration = 2 if event_label.lower() in ['workshop', 'exam', 'seminar', 'hackathon'] else 1
            
            return {
                "summary": f"[{event_label}] {email_subject}",
                "start": parsed_date,
                "end": parsed_date + datetime.timedelta(hours=duration),
                "type": event_label,
                "description": email_subject
            }
    return None