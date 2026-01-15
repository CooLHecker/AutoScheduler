import dateparser
import datetime
import re

ACADEMIC_KEYWORDS = [
    "assignment", "exam", "submission", "project", "viva", "quiz", 
    "workshop", "seminar", "session", "lecture", "bee", "fem", "physics"
]

MY_TIMEZONE = 'Asia/Kolkata'

def extract_academic_event(text):
    
    clean_text = " ".join(text.split())
    
    
    found_keyword = next((kw.capitalize() for kw in ACADEMIC_KEYWORDS if kw.lower() in clean_text.lower()), "Academic")
            
    
    date_time_pattern = r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+at\s+\d{1,2}(?::\d{2})?\s*[ap]m)?)"
    
    match = re.search(date_time_pattern, clean_text, re.IGNORECASE)
    
    
    search_chunk = match.group(0) if match else clean_text

    parsed_date = dateparser.parse(search_chunk, settings={
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.datetime.now(),
        'TIMEZONE': MY_TIMEZONE,
        'RETURN_AS_TIMEZONE_AWARE': False,
        'DATE_ORDER': 'DMY'
    })

    if parsed_date:
        
        if parsed_date.year < 2025:
            parsed_date = parsed_date.replace(year=2025)

       
        title_part = text.split("|")[0].strip()
        
        return {
            "summary": f"[{found_keyword}] {title_part}",
            "start": parsed_date,
            "end": parsed_date + datetime.timedelta(hours=1),
            "type": found_keyword,
            "description": f"Extracted from: {search_chunk}"
        }
    
    return None
