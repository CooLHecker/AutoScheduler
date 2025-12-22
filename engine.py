import dateparser
import datetime
import re

ACADEMIC_KEYWORDS = [
    "assignment", "exam", "submission", "project", "viva", "quiz", 
    "workshop", "seminar", "session", "lecture", "bee", "fem", "physics"
]

MY_TIMEZONE = 'Asia/Kolkata'

def extract_academic_event(text):
    # Standardize text (important for 'at 5pm' formats)
    clean_text = " ".join(text.split())
    
    # 1. Keyword Check
    found_keyword = next((kw.capitalize() for kw in ACADEMIC_KEYWORDS if kw.lower() in clean_text.lower()), "Academic")
            
    # 2. Advanced Regex to capture "25th December at 5pm" or "22 december"
    # This captures the date AND the following 'at Xpm' if it exists
    date_time_pattern = r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+at\s+\d{1,2}(?::\d{2})?\s*[ap]m)?)"
    
    match = re.search(date_time_pattern, clean_text, re.IGNORECASE)
    
    # If regex finds a match, we parse ONLY that match for maximum precision
    search_chunk = match.group(0) if match else clean_text

    parsed_date = dateparser.parse(search_chunk, settings={
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.datetime.now(),
        'TIMEZONE': MY_TIMEZONE,
        'RETURN_AS_TIMEZONE_AWARE': False,
        'DATE_ORDER': 'DMY'
    })

    if parsed_date:
        # If the email is for "Today" (Dec 22), ensure the year is 2025
        if parsed_date.year < 2025:
            parsed_date = parsed_date.replace(year=2025)

        # Clean up the title for the calendar
        title_part = text.split("|")[0].strip()
        
        return {
            "summary": f"[{found_keyword}] {title_part}",
            "start": parsed_date,
            "end": parsed_date + datetime.timedelta(hours=1),
            "type": found_keyword,
            "description": f"Extracted from: {search_chunk}"
        }
    
    return None