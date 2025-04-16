from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

RISK_FILE = "risks.json"

# Load existing risks or create empty file
if not os.path.exists(RISK_FILE):
    with open(RISK_FILE, "w") as f:
        json.dump([], f)

def load_risks():
    with open(RISK_FILE, "r") as f:
        return json.load(f)

def save_risks(risks):
    with open(RISK_FILE, "w") as f:
        json.dump(risks, f, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/risk-register", methods=["GET", "POST"])
def risk_register():
    if request.method == "POST":
        new_risk = {
            "id": request.form.get("id"),
            "description": request.form.get("description"),
            "impact": request.form.get("impact"),
            "likelihood": request.form.get("likelihood")
        }
        risks = load_risks()
        risks.append(new_risk)
        save_risks(risks)
        return redirect(url_for("risk_register"))

    risks = load_risks()
    return render_template("risk_register.html", risks=risks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
