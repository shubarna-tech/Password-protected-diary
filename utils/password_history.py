import json
import os

HISTORY_FILE = 'data/password_history.json'


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def is_password_reused(new_password):
    return new_password in load_history()

def update_history(new_password):
    history = load_history()
    history.append(new_password)
    save_history(history)
