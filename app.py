from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import sqlite3
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a strong random secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for login
class User(UserMixin):
    def __init__(self, id_, username, password):
        self.id = id_
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('risk_register.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# DB Setup
def init_db():
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS risks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        impact TEXT,
                        likelihood TEXT,
                        mitigation TEXT,
                        status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    # Default user (username: admin, password: admin123)
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ('admin', generate_password_hash('admin123')))
    conn.commit()
    conn.close()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('risk_register.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (request.form['username'],))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], request.form['password']):
            login_user(User(user[0], user[1], user[2]))
            return redirect('/risk-register')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/risk-register', methods=['GET', 'POST'])
@login_required
def risk_register():
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("INSERT INTO risks (title, description, impact, likelihood, mitigation, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (request.form['title'], request.form['description'], request.form['impact'],
                        request.form['likelihood'], request.form['mitigation'], request.form['status']))
        conn.commit()
    cursor.execute("SELECT * FROM risks")
    risks = cursor.fetchall()
    conn.close()
    return render_template('risk_register.html', risks=risks)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_risk(id):
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("""UPDATE risks SET title=?, description=?, impact=?, likelihood=?, 
                          mitigation=?, status=? WHERE id=?""",
                       (request.form['title'], request.form['description'], request.form['impact'],
                        request.form['likelihood'], request.form['mitigation'], request.form['status'], id))
        conn.commit()
        conn.close()
        return redirect('/risk-register')
    cursor.execute("SELECT * FROM risks WHERE id=?", (id,))
    risk = cursor.fetchone()
    conn.close()
    return render_template('edit_risk.html', risk=risk)

@app.route('/delete/<int:id>')
@login_required
def delete_risk(id):
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM risks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/risk-register')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM risks GROUP BY status")
    data = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in data]
    counts = [row[1] for row in data]

    return render_template('dashboard.html', labels=labels, counts=counts)

@app.route('/export')
@login_required
def export_csv():
    conn = sqlite3.connect('risk_register.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risks")
    risks = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Description', 'Impact', 'Likelihood', 'Mitigation', 'Status'])
    for row in risks:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='risk_register.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

