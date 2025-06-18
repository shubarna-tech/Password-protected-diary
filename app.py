from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import json
import os
from datetime import datetime
from utils.encryption import encrypt_data, decrypt_data

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATA_FILE = 'data/entries.json'
PASSWORD_FILE = 'data/password.txt'
DEFAULT_PASSWORD = '1234'

class User(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    return User()

def load_password():
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'w') as f:
            f.write(DEFAULT_PASSWORD)
    with open(PASSWORD_FILE, 'r') as f:
        return f.read().strip()

def save_password(new_password):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(new_password)

def read_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'rb') as f:
        encrypted = f.read()
        if not encrypted:
            return []
        try:
            decrypted = decrypt_data(encrypted, load_password().encode())
            return json.loads(decrypted)
        except Exception as e:
            print("InvalidToken error: Encrypted file does not match current password.")
            return []


def save_entries(entries):
    encrypted = encrypt_data(json.dumps(entries), load_password().encode())
    with open(DATA_FILE, 'wb') as f:
        f.write(encrypted)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == load_password():
            login_user(User())
            return redirect(url_for('diary'))
        else:
            flash('Wrong password!')
    return render_template('login.html')

@app.route('/diary')
@login_required
def diary():
    entries = read_entries()
    return render_template('diary.html', entries=entries)

@app.route('/add', methods=['POST'])
@login_required
def add():
    text = request.form['text']
    entries = read_entries()
    entries.append({
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_entries(entries)
    return redirect(url_for('diary'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
@login_required
def edit(index):
    entries = read_entries()
    if request.method == 'POST':
        entries[index]['text'] = request.form['text']
        entries[index]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_entries(entries)
        return redirect(url_for('diary'))
    return render_template('edit.html', entry=entries[index], index=index)

@app.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete(index):
    entries = read_entries()
    if 0 <= index < len(entries):
        entries.pop(index)
    save_entries(entries)
    return redirect(url_for('diary'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form['current']
        new = request.form['new']
        if current == load_password():
            # Read and decrypt entries using old password
            try:
                with open(DATA_FILE, 'rb') as f:
                    encrypted = f.read()
                decrypted = decrypt_data(encrypted, current.encode())
                entries = json.loads(decrypted)
            except Exception:
                flash('Failed to decrypt entries.')
                return redirect(url_for('change_password'))

            # Save new password
            save_password(new)

            # Re-encrypt entries with new password
            new_encrypted = encrypt_data(json.dumps(entries), new.encode())
            with open(DATA_FILE, 'wb') as f:
                f.write(new_encrypted)

            flash('Password changed successfully.')
            return redirect(url_for('diary'))
        else:
            flash('Current password is incorrect.')
    return render_template('change_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)
