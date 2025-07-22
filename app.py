from flask import Flask, render_template, request, send_file
import subprocess
import tempfile
import os
import json
from fpdf import FPDF

app = Flask(__name__)

def analyze_code(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp:
        temp.write(code)
        temp.flush()
        temp_path = temp.name

    try:
        pylint_output = subprocess.check_output(
            ['pylint', temp_path, '--output-format=json'],
            stderr=subprocess.STDOUT,
            text=True
        )
        results = json.loads(pylint_output)
    except subprocess.CalledProcessError as e:
        results = json.loads(e.output)
    finally:
        import time
        time.sleep(0.5)
        try:
            os.unlink(temp_path)
        except PermissionError:
            pass

    score = 10.0
    issues = []
    for item in results:
        issues.append({
            "type": item.get("type", "unknown"),
            "line": item.get("line", "N/A"),
            "message": item.get("message", "")
        })

    return {
        "score": round(score - len(issues)*0.5, 2),
        "total_issues": len(issues),
        "issues": issues
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.py'):
            code = file.read().decode('utf-8')
            report = analyze_code(code)

            # Save PDF to uploads/report.pdf
            os.makedirs("uploads", exist_ok=True)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Code Quality Audit Report", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Score: {report['score']}/10", ln=True)
            pdf.cell(200, 10, txt=f"Total Issues: {report['total_issues']}", ln=True)
            pdf.ln(5)
            for issue in report['issues']:
                line = f"{issue['type']} on line {issue['line']}: {issue['message']}"
                pdf.multi_cell(0, 10, txt=line)
            pdf.output("uploads/report.pdf")

    return render_template('index.html', report=report)

@app.route("/download-pdf")
def download_pdf():
    path = "uploads/report.pdf"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return "PDF not found. Please generate the report first.", 404
    try:
        return send_file(
            path,
            as_attachment=True,
            download_name="code_report.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error sending file: {e}")
        return f"Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
