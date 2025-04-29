import streamlit as st
import pandas as pd
import requests
import pickle
from utils import set_bg_hack, load_css
from config import BACKGROUND_IMAGE_PATH, DATA_PATH, MODEL_PATH
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Configuration de la page
st.set_page_config(
    page_title="CarPricer Morocco",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Charger CSS
load_css("styles.css")

# Charger le modèle et les préprocesseurs
@st.cache_resource
def load_model():
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    return model

model = load_model()

# Charger les données
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    # Créer la colonne 'age' dans le DataFrame original
    data['age'] = 2025 - data['Année-Modèle']
    data['Prix_par_km'] = 0  # Valeur par défaut
    data['Age_par_CV'] = data['age'] / data['Puissance fiscale']
    return data
 
try:
    df = load_data()
    
    # Extraire les options dynamiques
    marques = ["Sélectionner une marque"] + sorted(df["Marque"].dropna().unique().tolist())
    carburants = ["Sélectionner un carburant"] + sorted(df["Carburant_simplifié"].dropna().unique().tolist())
    couleurs = ["Sélectionner une couleur"] + sorted(df["couleur"].dropna().unique().tolist())
    villes = ["Sélectionner une ville"] + sorted(df["Ville"].dropna().unique().tolist())
    etats = ["Sélectionner un état", "Correct", "Excellent", "Neuf", "Pour Pièces", "Très bon"]
    origines = ["Sélectionner une origine", "Importée neuve", "Pas encore dédouanée", "WW au Maroc"]
    
    # Créer le mapping marque-modèles
    modeles_par_marque = {}
    for marque in df["Marque"].unique():
        modeles_par_marque[marque] = ["Sélectionner un modèle"] + sorted(df[df["Marque"] == marque]["Modèle"].dropna().unique().tolist())
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {str(e)}")
    st.stop()

# Charger l'image d'arrière-plan
try:
    set_bg_hack(BACKGROUND_IMAGE_PATH)
except:
    pass

# Header
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/3.5.0/css/flag-icon.min.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
            
    <header class="app-header">
        <div class="logo-container">
            <div class="app-logo">
                <span class="logo-car">Car</span>
                <span class="logo-pricer">Pricer</span>
            </div>
            <div class="nav-items">
             <a href="#">Research</a>
             <a href="#">Simulate</a>
             <a href="#">Get informed</a>
            </div>  
        </div>
        <div class="right-section">
            <a href="#"><i class="far fa-star"></i></a>
            <a href="#"><i class="far fa-bell"></i></a>  
            <div class="flag">
                <i class="flag-icon flag-icon-ma"></i>
             </div>     
        </div>     
    </header>
""", unsafe_allow_html=True)

# Initialiser les variables de session si elles n'existent pas
if 'marque' not in st.session_state: 
    st.session_state.marque = "Sélectionner une marque" 

if 'estimation_faite' not in st.session_state:
    st.session_state.estimation_faite = False

# Initialisation des variables de résultat
if 'prix' not in st.session_state:
    st.session_state.prix = None
    st.session_state.input_data = None



# Titre de la page avant le formulaire
st.markdown("""
<div class="page-title">
            <div class="landing-container">
                <div class="landing-title"><h1>CarPricer Morocco</h1>Estimez le prix de votre voiture au Maroc en quelques clics. 
            Notre système intelligent utilise les données du marché marocain pour vous fournir une estimation précise et fiable.</div>
            </div>
    <i class="fas fa-calculator" style="margin-right: 10px;"></i>
    Your Vehicle Price Simulator Guide
</div>
""", unsafe_allow_html=True)

# Section du formulaire (toujours affichée)
with st.container():
    st.markdown('<div class="input-container marque-selector">', unsafe_allow_html=True)
    
    # Titre avec classe CSS
    st.markdown('<label class="input-label">Marque du véhicule</label>', unsafe_allow_html=True)
    
    # Selectbox de marque
    marque = st.selectbox(
        label="", 
        options=marques,
        key="marque_selectbox",
        index=0 if st.session_state.marque == "Sélectionner une marque" else marques.index(st.session_state.marque)
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
# Déterminer les modèles disponibles en fonction de la marque sélectionnée
if marque and marque != "Sélectionner une marque":
    modele_options = modeles_par_marque.get(marque, ["Sélectionner un modèle"])
else:
    modele_options = ["Sélectionner un modèle"]

# Formulaire principal
with st.form("estimation_form"):
    st.markdown("""
        <div class="form-header">
            <i class="fas fa-car-side"></i>
            Entrez les caractéristiques de votre véhicule pour obtenir une estimation de prix
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
     
    with col1:
        # La marque est maintenant en dehors du formulaire, mais nous la conservons dans le formulaire
        # pour que l'utilisateur puisse voir sa sélection
        marque_display = st.text_input("Marque sélectionnée", value=marque, disabled=True)
        
        carburant = st.selectbox("Type de carburant", carburants)
        km = st.number_input("Kilométrage", min_value=0, value=50000)
        ville = st.selectbox("Ville", villes)

    with col2:
        # Affichage des modèles basés sur la marque sélectionnée
        modele = st.selectbox("Modèle", modele_options)
        
        boite = st.selectbox("Boîte de vitesses", ["Sélectionner une boîte", "Manuelle", "Automatique"])
        portes = st.number_input("Nombre de portes", min_value=2, max_value=5, value=4)
        origine = st.selectbox("Origine", origines)
    
    with col3:
        annee = st.number_input("Année du véhicule", min_value=1990, max_value=2025, value=2015)
        puissance = st.number_input("Puissance fiscale (CV)", min_value=1, value=6)
        couleur = st.selectbox("Couleur", couleurs)
        etat = st.selectbox("État du véhicule", etats)

    submitted = st.form_submit_button("Estimer")

# Fonction de prédiction MODIFIÉE
def predict_price(input_data):
    try:
        # Préparation des données
        input_df = pd.DataFrame([input_data])
        
        # Calculer les variables dérivées avant l'encodage
        input_df['age'] = 2025 - input_df['Année-Modèle']
        input_df['Car_age'] = input_df['age']  # Add this since your model expects it
        input_df['Prix_par_km'] = 0  # Valeur par défaut
        input_df['Age_par_CV'] = input_df['age'] / input_df['Puissance fiscale']
        
        # Add missing features with default values
        if 'Première main' not in input_df:
            input_df['Première main'] = 0  # Default value
        
        # Add frequency features from the original dataset
        for col in ['Marque', 'Modèle', 'Ville', 'Carburant_simplifié', 'couleur']:
            freq_col = f"{col}_freq"
            input_df[freq_col] = input_df[col].map(df[col].value_counts(normalize=True).to_dict())
            # Fill NaN values with a small frequency
            input_df[freq_col] = input_df[freq_col].fillna(0.001)
        
        # One-hot encode categorical variables instead of label encoding
        # For 'Boite de vitesses'
        input_df['Boite de vitesses_Manuelle'] = (input_df['Boite de vitesses'] == 'Manuelle').astype(int)
        
        # For 'Origine'
        for cat in ['Importée neuve', 'Pas encore dédouanée', 'WW au Maroc']:
            input_df[f'Origine_{cat}'] = (input_df['Origine'] == cat).astype(int)
        
        # For 'État'
        for cat in ['Correct', 'Excellent', 'Neuf', 'Pour Pièces', 'Très bon']:
            input_df[f'État_{cat}'] = (input_df['État'] == cat).astype(int)
        
        # Create a list of features in the exact order the model expects
        expected_features = ['Année-Modèle', 'Kilométrage', 'Nombre de portes', 'Première main', 
                             'Puissance fiscale', 'Car_age', 'Boite de vitesses_Manuelle', 
                             'Origine_Importée neuve', 'Origine_Pas encore dédouanée', 
                             'Origine_WW au Maroc', 'État_Correct', 'État_Excellent', 
                             'État_Neuf', 'État_Pour Pièces', 'État_Très bon', 'Marque_freq', 
                             'Modèle_freq', 'Ville_freq', 'Carburant_simplifié_freq', 
                             'couleur_freq', 'age', 'Prix_par_km', 'Age_par_CV']
        
        # Ensure all expected features exist
        for feat in expected_features:
            if feat not in input_df.columns:
                input_df[feat] = 0  # Default for missing columns
        
        # Select only the expected columns in the right order
        prediction_df = input_df[expected_features]
        
        # Prédiction
        prediction = model.predict(prediction_df)
        return prediction[0]
    except Exception as e:
        st.error(f"Erreur lors de la prédiction: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Traitement du formulaire de prédiction
if submitted:
    if marque == "Sélectionner une marque" or modele == "Sélectionner un modèle":
        st.warning("Veuillez sélectionner une marque et un modèle valides")
    else:
        st.session_state.input_data = {
            'Marque': marque,
            'Modèle': modele,
            'Carburant_simplifié': carburant,
            'Ville': ville,
            'couleur': couleur,
            'Boite de vitesses': boite,
            'Origine': origine,
            'État': etat,
            'Nombre de portes': portes,
            'Kilométrage': km,
            'Année-Modèle': annee,
            'Puissance fiscale': puissance
        }
        
        with st.spinner('Calcul en cours...'):
            st.session_state.prix = predict_price(st.session_state.input_data)
        
        st.session_state.estimation_faite = True

# Affichage du résultat si l'estimation a été faite
if st.session_state.estimation_faite and st.session_state.prix is not None:
    input_data = st.session_state.input_data
    prix = st.session_state.prix
    
st.markdown(f"""
    <div class="result-container">
        <div class="result-icon"><i class="fas fa-tag"></i></div>
        <div class="result-title">Prix estimé</div>
        <div class="result-price">{prix:,.0f} MAD</div>
        <div class="price-range">
            <div class="range-low">Prix bas: {max(0, prix*0.9):,.0f} MAD</div>
            <div class="range-high">Prix haut: {prix*1.1:,.0f} MAD</div>
        </div>
        <div class="result-title">Information Sur La Voiture Sélectionnée</div>
        <div class="price-range">
            <div class="range-low">La Marque: {input_data['Marque']} </div>
            <div class="range-high">Le Modèle: {input_data['Modèle']} </div>
            <div class="range-high">Le Type de Carburant: {input_data['Carburant_simplifié']} </div>
            <div class="range-high">Le Type de Boite Vitesse: {input_data['Boite de vitesses']}</div>
            <div class="range-high">Kilométrage: {input_data['Kilométrage']} KM</div>
            <div class="range-high">Le Nombre des Portes: {input_data['Nombre de portes']} </div>
            <div class="range-high">Le Nombre d'année du Modèle: {input_data['Année-Modèle']}</div>
            <div class="range-high">La Puissance Fiscale: {input_data['Puissance fiscale']} (CV)</div>
            <div class="range-high">La Couleur: {input_data['couleur']} </div>
            <div class="range-high">La Ville: {input_data['Ville']} - MAROC</div>
        </div>
        <div class="result-disclaimer">Estimation indicative basée sur Les critères de la voiture</div>

    </div>
""", unsafe_allow_html=True)

# 1. Générer le contenu du rapport
rapport_content = f"""
--- RAPPORT D'ESTIMATION DE VOTRE VOITURE ---

Prix Estimé: {prix:,.0f} MAD
Prix Bas Estimé: {max(0, prix*0.9):,.0f} MAD
Prix Haut Estimé: {prix*1.1:,.0f} MAD

--- Informations sur le véhicule ---

Marque: {input_data['Marque']}
Modèle: {input_data['Modèle']}
Carburant: {input_data['Carburant_simplifié']}
Boîte de vitesses: {input_data['Boite de vitesses']}
Kilométrage: {input_data['Kilométrage']} KM
Nombre de portes: {input_data['Nombre de portes']}
Année du modèle: {input_data['Année-Modèle']}
Puissance fiscale: {input_data['Puissance fiscale']} CV
Couleur: {input_data['couleur']}
Ville: {input_data['Ville']} - Maroc

--- Remarque ---
Estimation indicative basée sur les caractéristiques fournies.
"""

# 2. Ajouter le bouton de téléchargement

st.download_button(
    label="Télécharger le rapport",
    data=rapport_content,
    file_name="rapport_estimation.txt",
    mime="text/plain",
    key="download-report"
)


# Pied de page (toujours affiché)
st.markdown("""
    <div class="footer">
        <div class="footer-container">
            <div class="footer-logo">
                <div class="footer-logo-text">
                    <span class="footer-logo-car">Car</span>
                    <span>Pricer</span>
                </div>
                <div class="footer-tagline">Votre guide d'estimation automobile au Maroc</div>
            </div>
        </div>
        <div class="footer-copyright">© 2025 CarPricer Morocco. Tous droits réservés.</div>
    </div>
""", unsafe_allow_html=True)

# Ajouter JavaScript pour les animations et le téléchargement du rapport
st.markdown("""
<script>
    // Fonction pour télécharger le rapport (simulée)
    function downloadReport() {
        // Création d'un PDF simulé
        alert('Le rapport va être téléchargé...');
        
        // Dans une vraie application, vous utiliseriez une bibliothèque PDF
        // comme jsPDF ou vous appelleriez une API backend
        
        // Simulation d'un délai de téléchargement
        setTimeout(function() {
            // Créer un élément <a> invisible et déclencher le téléchargement
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = 'data:application/pdf;base64,JVBERi0xLjMNCiXi48/TDQoxIDAgb2JqDQo8PCAvVHlwZSAvQ2F0YWxvZw0KL091dGxpbmVzIDIgMCBSDQovUGFnZXMgMyAwIFIgPj4NCmVuZG9iag0KMiAwIG9iag0KPDwgL1R5cGUgL091dGxpbmVzIC9Db3VudCAwID4+DQplbmRvYmoNCjMgMCBvYmoNCjw8IC9UeXBlIC9QYWdlcw0KL0tpZHMgWzYgMCBSCl0NCi9Db3VudCAxDQovUmVzb3VyY2VzIDw8DQovUHJvY1NldCA0IDAgUiANCi9Gb250IDw8IA0KL0YxIDggMCBSIA0KL0YyIDkgMCBSIA0KPj4NCj4+DQovTWVkaWFCb3ggWzAuMDAwIDAuMDAwIDYxMi4wMDAgNzkyLjAwMF0NCiA+Pg0KZW5kb2JqDQo0IDAgb2JqDQpbL1BERiAvVGV4dCBdDQplbmRvYmoNCjUgMCBvYmoNCjw8DQovQ3JlYXRvciAoUmVwb3J0IENhclByaWNlcikNCi9Qcm9kdWNlciAoQ2FyUHJpY2VyKQ0KL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDQyODEyMDAwMCkNCj4+DQplbmRvYmoNCjYgMCBvYmoNCjw8IC9UeXBlIC9QYWdlIA0KL1BhcmVudCAzIDAgUiANCi9Db250ZW50cyAxMCAwIFIgDQo+Pg0KZW5kb2JqDQoxMCAwIG9iag0KPDwgL0ZpbHRlciAvRmxhdGVEZWNvZGUgDQovTGVuZ3RoIDEwMCkNCnN0cmVhbXgm5YvRjsIwDEQv+8K4cCsAAAAAAAAAAAAAAAAAAAAAAAAA19DSM151Tx0=';
            a.download = 'rapport_voiture_carpricer.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }, 1000);
    }
    
    // Ajouter des effets d'animation si nécessaire
    document.addEventListener('DOMContentLoaded', function() {
        // Animation pour le bouton ESSAYER MAINTENANT
        const tryNowBtn = document.querySelector('.try-now-button-container button');
        if (tryNowBtn) {
            tryNowBtn.addEventListener('mouseover', function() {
                this.style.transform = 'scale(1.05)';
            });
            tryNowBtn.addEventListener('mouseout', function() {
                this.style.transform = 'scale(1)';
            });
        }
    });
</script>
""", unsafe_allow_html=True)