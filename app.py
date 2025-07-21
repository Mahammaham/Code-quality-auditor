from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def run_pylint(file_path):
    try:
        result = subprocess.run(['pylint', file_path], capture_output=True, text=True)
        output = result.stdout
        score_line = [line for line in output.split('\n') if 'Your code has been rated at' in line]
        score = float(score_line[0].split(' ')[6].split('/')[0]) if score_line else 0.0
        return output, score
    except Exception as e:
        return str(e), 0.0

def generate_recommendations(output):
    recommendations = []
    if "missing-docstring" in output:
        recommendations.append("Add docstrings to your functions and classes.")
    if "unused-import" in output:
        recommendations.append("Remove unused imports.")
    if "line-too-long" in output:
        recommendations.append("Break long lines into multiple lines.")
    if "too-many-locals" in output:
        recommendations.append("Refactor functions with too many local variables.")
    return recommendations or ["Great job! Your code looks clean."]

def create_pdf_report(score, recommendations, output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Code Quality Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Score: {score}/100", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Recommendations:", ln=True)
    for r in recommendations:
        pdf.multi_cell(0, 10, txt=f"- {r}")
    pdf.ln(5)
    pdf.cell(200, 10, txt="Detailed Pylint Output:", ln=True)
    pdf.set_font("Arial", size=10)
    for line in output.splitlines():
        pdf.multi_cell(0, 5, txt=line)
    report_path = os.path.join("uploads", "report.pdf")
    pdf.output(report_path)
    return report_path

@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    result = None
    recommendations = []
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            result, score = run_pylint(filepath)
            recommendations = generate_recommendations(result)
            create_pdf_report(score, recommendations, result)
    return render_template("index.html", score=score, result=result, recommendations=recommendations)

@app.route("/download-pdf")
def download_pdf():
    return send_file("uploads/report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5050)

