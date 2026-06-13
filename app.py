from flask import Flask, render_template, request, send_file, jsonify
from facture import generer_facture
import tempfile
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Liste de produits en mémoire
products = [
    {"name": "Produit Exemple 1", "price": 10.00},
    {"name": "Produit Exemple 2", "price": 20.00},
    {"name": "Produit Exemple 3", "price": 30.00},
    {"name": "Produit Exemple 4", "price": 40.00}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        data = request.get_json()
        products.append({"name": data['name'], "price": float(data['price'])})
        return jsonify({"status": "success"})
    return jsonify(products)

@app.route('/products/<name>', methods=['DELETE'])
def delete_product(name):
    global products
    products = [p for p in products if p['name'] != name]
    return jsonify({"status": "success"})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    # Générer un identifiant court (6 caractères)
    short_uuid = uuid.uuid4().hex[:6]
    # Date du jour au format YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Construire le nom de fichier
    filename = f"factures_{today}_{short_uuid}.pdf"
    # Chemin temporaire
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    # Générer la facture
    generer_facture(data, temp_path)
    # Retourner le fichier avec un nom convivial
    return send_file(temp_path, as_attachment=True, download_name=filename, mimetype="application/pdf")

if __name__ == '__main__':
    # Configuration spécifique pour l'hébergement (Render, Heroku, etc.)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
