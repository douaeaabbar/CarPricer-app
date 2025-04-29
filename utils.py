import streamlit as st
import base64
import pandas as pd
from PIL import Image
import io

def set_bg_hack(main_bg):
    """
    Une fonction pour définir l'image d'arrière-plan d'une application streamlit
    Args:
        main_bg (str): Chemin vers l'image d'arrière-plan
    """
    main_bg_ext = "png" if 'png' in main_bg else "jpg"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_model_by_marque(df, marque):
    """
    Obtenir la liste des modèles pour une marque donnée
    Args:
        df (pandas.DataFrame): DataFrame contenant les données
        marque (str): Nom de la marque
    Returns:
        list: Liste des modèles pour la marque spécifiée
    """
    return df[df['Marque']==marque]['Modèle'].dropna().unique().tolist()

def load_css(css_file):
    """
    Charger un fichier CSS dans Streamlit
    Args:
        css_file (str): Chemin vers le fichier CSS
    """
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)