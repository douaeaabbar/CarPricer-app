from flask import Flask, request, jsonify
import pandas as pd
import joblib
from config import MODEL_PATH, DATA_PATH

app = Flask(__name__)

# Charger les données et le modèle
df = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)
modeles_par_marque = df.groupby("Marque")["Modèle"].unique().apply(list).to_dict()

@app.route('/get_modeles', methods=['GET'])
def get_modeles():
    marque = request.args.get('marque')
    if marque in modeles_par_marque:
        return jsonify(sorted(modeles_par_marque[marque]))
    return jsonify([])

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Préparation des données comme dans votre code original
    etats = ["Correct", "Excellent", "Neuf", "Pour Pièces", "Très bon"]
    origines = ["Importée neuve", "Pas encore dédouanée", "WW au Maroc"]
    
    etat_columns = {f"État_{e}": [1 if e == data['etat'] else 0] for e in etats}
    origine_columns = {f"Origine_{o}": [1 if o == data['origine'] else 0] for o in origines}

    input_data = {
        "Année-Modèle": [2025 - data['annee']],
        "Kilométrage": [data['km']],
        "Nombre de portes": [data['portes']],
        "Première main": [0],
        "Puissance fiscale": [data['puissance']],
        "Car_age": [data['annee']],
        "Boite de vitesses_Manuelle": [1 if data['boite'] == "Manuelle" else 0],
        "Marque_freq": [data['marque']],
        "Modèle_freq": [data['modele']],
        "Ville_freq": [data['ville']],
        "Carburant_simplifié_freq": [data['carburant']],
        "couleur_freq": [data['couleur']],
        "Prix_par_km": [0],
        "Age_par_CV": [data['annee'] / data['puissance'] if data['puissance'] > 0 else 0]
    }

    input_data.update(etat_columns)
    input_data.update(origine_columns)

    input_df = pd.DataFrame(input_data)

    # Gérer les colonnes manquantes
    missing_cols = set(df.columns) - set(input_df.columns)
    for col in missing_cols:
        if col != "Prix":
            input_df[col] = 0

    model_columns = [col for col in df.columns if col != "Prix"]
    input_df = input_df[model_columns]

    # Faire la prédiction
    prediction = model.predict(input_df)[0]
    
    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(debug=True, port=5000)