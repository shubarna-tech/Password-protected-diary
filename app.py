from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from config import SESSION_TIMEOUT_MINUTES
from utils.twofa import generate_otp, validate_otp
from utils.password_history import is_password_reused, update_history
from utils.encryption import encrypt_data, decrypt_data
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

EDIT_HISTORY_FILE = 'data/edit_history.json'
UPLOAD_FOLDER = 'data/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

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
        except Exception:
            print("Decryption failed.")
            return []

def save_entries(entries):
    encrypted = encrypt_data(json.dumps(entries), load_password().encode())
    with open(DATA_FILE, 'wb') as f:
        f.write(encrypted)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['temp_email'] = email
        session['temp_password'] = password
        if password == load_password():
            otp = generate_otp(email)
            print(f"[DEBUG] OTP for {email}: {otp}")
            return redirect(url_for('verify_otp'))
        else:
            flash('Wrong password!')
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('temp_email')
    if request.method == 'POST':
        user_otp = request.form['otp']
        if validate_otp(email, user_otp):
            login_user(User())
            return redirect(url_for('diary'))
        else:
            return render_template('2fa.html', message='Invalid OTP')
    return render_template('2fa.html', message='OTP printed in terminal')

@app.route('/diary')
@login_required
def diary():
    entries = read_entries()
    
    # SORTING
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'oldest':
        entries.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_by == 'title-az':
        entries.sort(key=lambda x: x.get('title', '').lower())
    elif sort_by == 'title-za':
        entries.sort(key=lambda x: x.get('title', '').lower(), reverse=True)
    else:  # Default: newest
        entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    # PAGINATION
    page = int(request.args.get('page', 1))
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated = entries[start:end]
    total_pages = (len(entries) + per_page - 1) // per_page

    return render_template(
        'diary.html',
        entries=paginated,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by
    )

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').lower()
    date_filter = request.args.get('date', '')
    sort_by = request.args.get('sort', 'newest')
    page = int(request.args.get('page', 1))
    per_page = 5

    all_entries = read_entries()
    filtered = []

    for entry in all_entries:
        match_text = query in entry.get('title', '').lower() or \
                     query in entry.get('text', '').lower() or \
                     query in entry.get('tags', '').lower()
        match_date = date_filter in entry.get('timestamp', '') if date_filter else True
        if match_text and match_date:
            filtered.append(entry)

    # Apply sorting
    if sort_by == 'oldest':
        filtered.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_by == 'title-az':
        filtered.sort(key=lambda x: x.get('title', '').lower())
    elif sort_by == 'title-za':
        filtered.sort(key=lambda x: x.get('title', '').lower(), reverse=True)
    else:
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    total_pages = (len(filtered) + per_page - 1) // per_page

    flash(f"Found {len(filtered)} result(s) for query.")
    return render_template(
        'diary.html',
        entries=paginated,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        search_active=True
    )


@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    text = request.form['text']
    tags = request.form.get('tags', '')
    mood = request.form.get('mood', '')
    image_url = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = url_for('uploaded_file', filename=filename)
    entries = read_entries()
    entries.append({
        'title': title,
        'text': text,
        'tags': tags,
        'mood': mood,
        'image': image_url,
        'favorite': False,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_entries(entries)
    return redirect(url_for('diary'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
@login_required
def edit(index):
    entries = read_entries()
    if request.method == 'POST':
        history = read_history()
        entry_copy = entries[index].copy()
        entry_copy['edited_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history.setdefault(str(index), []).append(entry_copy)
        save_history(history)

        entries[index]['title'] = request.form['title']
        entries[index]['text'] = request.form['text']
        entries[index]['tags'] = request.form.get('tags', '')
        entries[index]['mood'] = request.form.get('mood', '')

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                entries[index]['image'] = url_for('uploaded_file', filename=filename)

        entries[index]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_entries(entries)
        return redirect(url_for('diary'))

    return render_template('edit.html', entry=entries[index], index=index)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form['current']
        new = request.form['new']
        if current == load_password():
            if is_password_reused(new):
                flash('Password already used. Choose a different one.')
                return redirect(url_for('change_password'))
            try:
                with open(DATA_FILE, 'rb') as f:
                    encrypted = f.read()
                decrypted = decrypt_data(encrypted, current.encode())
                entries = json.loads(decrypted)
            except Exception:
                flash('Failed to decrypt entries.')
                return redirect(url_for('change_password'))

            save_password(new)
            update_history(new)
            new_encrypted = encrypt_data(json.dumps(entries), new.encode())
            with open(DATA_FILE, 'wb') as f:
                f.write(new_encrypted)

            flash('Password changed successfully.')
            return redirect(url_for('diary'))
        else:
            flash('Current password is incorrect.')
    return render_template('change_password.html')

@app.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete(index):
    entries = read_entries()
    if 0 <= index < len(entries):
        entries.pop(index)
    save_entries(entries)
    return redirect(url_for('diary'))

@app.route('/favorite/<int:index>', methods=['POST'])
@login_required
def toggle_favorite(index):
    entries = read_entries()
    if 0 <= index < len(entries):
        current = entries[index].get('favorite', False)
        entries[index]['favorite'] = not current
        save_entries(entries)
    return redirect(url_for('diary'))

@app.route('/favorites')
@login_required
def view_favorites():
    entries = read_entries()
    favs = [e for e in entries if e.get('favorite')]

    # Apply same pagination/sorting logic
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'oldest':
        favs.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_by == 'title-az':
        favs.sort(key=lambda x: x.get('title', '').lower())
    elif sort_by == 'title-za':
        favs.sort(key=lambda x: x.get('title', '').lower(), reverse=True)
    else:
        favs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    page = int(request.args.get('page', 1))
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated = favs[start:end]
    total_pages = (len(favs) + per_page - 1) // per_page

    flash(f"{len(favs)} favorite entries found.")
    return render_template(
        'diary.html',
        entries=paginated,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        search_active=True
    )


@app.route('/history/<int:index>')
@login_required
def view_history(index):
    history = read_history()
    versions = history.get(str(index), [])
    return render_template('history.html', index=index, versions=versions)

def read_history():
    if not os.path.exists(EDIT_HISTORY_FILE):
        return {}
    with open(EDIT_HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history):
    with open(EDIT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)
