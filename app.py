from flask import Flask, render_template, request, send_file
from facture import generer_facture
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    temp_path = os.path.join(tempfile.gettempdir(), "facture.pdf")
    generer_facture(data, temp_path)
    return send_file(temp_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
