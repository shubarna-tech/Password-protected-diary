📝 Encrypted Diary Web App

A password-protected diary, web app where your thoughts are safely encrypted and stored locally.

🔐 Features

- Login system with encryption
- Add new diary pages
- View diary entry per page with number
- Edit entries on a separate page
- Change password securely
- Delete diary entries
- Date and time shown on top-right
- All data stored encrypted locally

 🛠 Tech Stack

- Python 3.x
- Flask
- Flask-Login
- Cryptography (Fernet encryption)
- HTML + CSS (diary design)

 🚀 Installation


# Step 2: Install Python Dependencies

Make sure Python is installed.
Then install the required packages:


bash
pip install flask flask-login cryptography


# Step 3: Folder Setup
Ensure the folder structure is like this:

diary_project/
├── app.py
├── data/
│   └── entries.json (auto-created)
├── utils/
│   └── encryption.py
├── templates/
│   ├── layout.html
│   ├── login.html
│   └── diary.html
├── static/
│   └── style.css
└── README.md

# Step 4: Run the App

bash
python app.py


# Step 5: Open Your Browser

Go to:http://localhost:5000

Login using the default password defined in `app.py`.

💡 Security Tip
Update the `PASSWORD` value inside `app.py` to your own secure password.
