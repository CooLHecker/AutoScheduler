# 🎓 AutoScheduler

AutoScheduler is a smart productivity tool that automatically "senses" academic events from your Gmail and syncs them to your Google Calendar. 

## 🚀 How it Works
1. **Connect:** Securely log in using your Google Account.
2. **Sense:** The engine scans your recent emails for keywords like *Assignment, Workshop, Exam, or Deadline*.
3. **Sync:** it extracts dates and creates a clean event in your Google Calendar with reminders.

## ✨ Features
- **Smart Filtering:** Only picks up academic-related emails.
- **Duplicate Prevention:** Won't clutter your calendar with the same event twice.
- **Clean Titles:** Uses email subjects for calendar entries, not messy snippets.
- **Production Ready:** Built for scale on Google Cloud Platform.

## 🛠️ Tech Stack
- **Language:** Python
- **Framework:** Streamlit
- **APIs:** Gmail API, Google Calendar API
- **Deployment:** GCP (OAuth2), Streamlit Cloud

## 🔧 Installation & Setup
1. Clone the repo: `git clone https://github.com/CooLHecker/AutoScheduler.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.streamlit/secrets.toml` with your Google Cloud Credentials.
4. Run the app: `streamlit run frontend.py`