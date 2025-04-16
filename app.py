from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy risk data
risks = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/risk_register', methods=['GET', 'POST'])
def risk_register():
    if request.method == 'POST':
        risk = {
            'id': len(risks) + 1,
            'name': request.form['risk_name'],
            'impact': request.form['impact'],
            'likelihood': request.form['likelihood']
        }
        risks.append(risk)
        return redirect(url_for('risk_register'))
    return render_template('risk_register.html', risks=risks)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', risks=risks)

if __name__ == '__main__':
    app.run(debug=True)
