📝 Encrypted Diary Web App

A password-protected diary web app where your thoughts are safely encrypted and stored locally.

🔐 Features

-Login system with encryption + OTP (terminal-based 2FA)

-Add new diary entries with title, tags, mood, and rich text

-View entries with page numbers and timestamps

-Edit diary entries with versioned edit history

-Mark entries as ⭐ Favorite / Unmark

-Attach images to entries

-Delete entries safely

-Change password securely (with reuse protection)

-Search entries by keyword, tag, or date

-Filter favorites and sort entries (Newest, A–Z, Z–A)

-Pagination for browsing entries

-Calendar picker for selecting date

-Dark Mode toggle (remembers your choice)

-Responsive design for mobile and desktop

-All data is encrypted and stored locally

🛠 Tech Stack

Backend: Python 3.x, Flask, Flask-Login

Encryption: cryptography (AES/Fernet)

Frontend: HTML, CSS, JavaScript, Quill Editor, Flatpickr

UI Libraries: Bootstrap-inspired alerts, dark mode via localStorage

🚀 Installation
Step 1: Clone the repository

bash
git clone https://github.com/your-username/encrypted-diary.git
cd encrypted-diary

Step 2: Install Python Dependencies
Make sure Python is installed. Then install the required packages:

bash
pip install flask flask-login cryptography

Step 3: Folder Setup
Ensure the folder structure is like this:

Step 4: Run the App

bash
python app.py

Step 5: Open Your Browser
Visit: http://localhost:5000

Login using the default password defined in app.py.

💡 Security Tip
After first login, use the Change Password feature to set a strong password.
The app tracks password history to prevent reuse and securely re-encrypts existing data.
