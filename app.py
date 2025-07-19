from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-lint', methods=['POST'])
def run_lint():
    result = subprocess.run(['pylint', 'example.py'], capture_output=True, text=True)
    return render_template('index.html', result=result.stdout)

@app.route('/run-tests', methods=['POST'])
def run_tests():
    result = subprocess.run(['pytest', '--tb=short'], capture_output=True, text=True)
    return render_template('index.html', result=result.stdout)

if __name__ == '__main__':
    app.run(debug=True)
