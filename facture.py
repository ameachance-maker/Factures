from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import qrcode
import tempfile
import uuid
app = Flask(__name__)

class FacturePDF(FPDF):
    def header(self):
        # Logo (remplace par ton logo.png si dispo)
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        self.set_font("TypeMachine", "", 20)
        self.cell(0, 10, "FACTURE", align="R", ln=1)
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font("TypeMachine", "", 8)
        self.set_text_color(120, 120, 120)
        self.multi_cell(0, 5, "Coordonnées bancaires :\nIBAN : FR76 3000 4000 5000 6000 7000 890\nBIC : BNPAFRPP\n\nMerci de régler votre facture sous 30 jours.\nMa Société • Adresse société • contact@masociete.com", align="C")

def generer_facture(data, output_path):
    pdf = FacturePDF()
    
    # Charger ta police AVANT d’ajouter une page
    pdf.add_font("TypeMachine", "", "Type_Machine.ttf", uni=True)
    pdf.set_font("TypeMachine", "", 12)

    # Maintenant ajouter une page (la police est dispo pour header/footer)
    pdf.add_page()

    # --- Bloc Société / Facture Info ---
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(100, 8, "Ma Société", ln=0, fill=True)
    pdf.cell(0, 8, f"Facture n° {data['numero']}", align="R", ln=1, fill=True)
    pdf.cell(100, 8, "Adresse société, Ville", ln=0, fill=True)
    pdf.cell(0, 8, f"Date : {data['date']}", align="R", ln=1, fill=True)
    pdf.ln(8)

    # --- Bloc Client ---
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, "Facturé à :", ln=1, fill=True)
    pdf.cell(0, 6, f"{data['client']}", ln=1)
    pdf.cell(0, 6, f"{data['adresse']}", ln=1)
    pdf.ln(10)

    # --- Tableau des articles ---
    pdf.set_font("TypeMachine", "", 12)
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)

    pdf.cell(80, 8, "Description", border=0, fill=True)
    pdf.cell(30, 8, "Quantité", border=0, align="C", fill=True)
    pdf.cell(40, 8, "Prix Unitaire (€)", border=0, align="R", fill=True)
    pdf.cell(40, 8, "Total (€)", border=0, align="R", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("TypeMachine", "", 11)

    total_ht = 0
    fill = False
    for article in data['articles']:
        desc = article['description']
        qty = article['quantite']
        price = article['prix']
        line_total = qty * price

        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        fill = not fill

        pdf.cell(80, 8, desc, border="B", fill=True)
        pdf.cell(30, 8, str(qty), border="B", align="C", fill=True)
        pdf.cell(40, 8, f"{price:.2f} €", border="B", align="R", fill=True)
        pdf.cell(40, 8, f"{line_total:.2f} €", border="B", align="R", fill=True)
        pdf.ln()
        total_ht += line_total

    # --- Totaux ---
    tva = total_ht * data['tva']
    total_ttc = total_ht + tva

    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("TypeMachine", "", 12)

    pdf.cell(150, 8, "Total HT", align="R")
    pdf.cell(40, 8, f"{total_ht:.2f} €", align="R", ln=1)

    pdf.cell(150, 8, f"TVA ({data['tva']*100:.0f}%)", align="R")
    pdf.cell(40, 8, f"{tva:.2f} €", align="R", ln=1)

    pdf.set_font("TypeMachine", "", 14)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(150, 10, "TOTAL TTC", align="R", fill=True)
    pdf.cell(40, 10, f"{total_ttc:.2f} €", align="R", fill=True, ln=1)

    # --- QR Code ---
    qr_data = f"Facture {data['numero']} - Client: {data['client']} - Total: {total_ttc:.2f} €"
    qr = qrcode.make(qr_data)
    temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    qr.save(temp_qr.name)

    pdf.image(temp_qr.name, x=170, y=pdf.get_y() + 15, w=30)

    pdf.output(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = {
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
    a=uuid.uuid4()
    a = a.hex[:6]
    output_path = os.path.join(os.getcwd(), f"Factures{a}.pdf")
    generer_facture(data, output_path)

    return send_file(output_path, as_attachment=True, mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True)
