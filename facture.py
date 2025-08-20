from flask import Flask, render_template, request, send_file
from datetime import datetime
from fpdf import FPDF
import os

app = Flask(__name__)

def generer_facture(data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # En-tête
    pdf.cell(200, 10, txt=f"Facture n° {data['numero']}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Client : {data['client']}", ln=True)
    pdf.cell(200, 10, txt=f"Adresse : {data['adresse']}", ln=True)
    pdf.cell(200, 10, txt=f"Date : {data['date']}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Articles :", ln=True)

    total_ht = 0
    for article in data['articles']:
        desc = article['description']
        qty = article['quantite']
        price = article['prix']
        line = f"{desc} - {qty} x {price:.2f} €"
        pdf.cell(200, 10, txt=line, ln=True)
        total_ht += qty * price

    tva = total_ht * data['tva']
    total_ttc = total_ht + tva

    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total HT : {total_ht:.2f} €", ln=True)
    pdf.cell(200, 10, txt=f"TVA ({data['tva']*100:.0f}%) : {tva:.2f} €", ln=True)
    pdf.cell(200, 10, txt=f"Total TTC : {total_ttc:.2f} €", ln=True)

    pdf.output(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = {
        'logo': '',  # À intégrer si tu veux ajouter un logo
        'client': request.form['client'],
        'adresse': request.form['adresse'],
        'date': request.form['date'],
        'numero': request.form['numero'],
        'articles': [],
        'tva': float(request.form['tva']) / 100
    }

    descriptions = request.form.getlist('description')
    quantites = request.form.getlist('quantite')
    prix_unitaires = request.form.getlist('prix')

    for desc, qty, price in zip(descriptions, quantites, prix_unitaires):
        data['articles'].append({
            'description': desc,
            'quantite': int(qty),
            'prix': float(price)
        })

    output_path = 'facture.pdf'
    generer_facture(data, output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
