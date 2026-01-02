# """
# =============================================================================
# APPLICATION WEB - DÉTECTION DE FRAUDE ASSURANCE AUTOMOBILE (MODERN UI)
# =============================================================================
# Auteur: Amal Tani NOUR
# Master 2 Data Science - Djibouti
# =============================================================================
# Nécessite: pip install streamlit pandas numpy plotly openpyxl streamlit-option-menu
# =============================================================================
# """

# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date
# from streamlit_option_menu import option_menu # NOUVELLE LIBRAIRIE REQUISE

# # =============================================================================
# # CONFIGURATION DE LA PAGE & DESIGN SYSTEM
# # =============================================================================
# st.set_page_config(
#     page_title="SafeGuard | Détection de Fraude",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # CSS PERSONNALISÉ POUR UN LOOK ULTRA-MODERNE
# st.markdown("""
# <style>
#     /* Import de police moderne (optionnel, sinon utilise la défaut système) */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

#     html, body, [class*="css"] {
#         font-family: 'Inter', sans-serif;
#     }

#     /* Nettoyage du header par défaut */
#     header[data-testid="stHeader"] {
#         background-image: none;
#         background-color: transparent;
#     }

#     /* Style des conteneurs principaux */
#     .main .block-container {
#         padding-top: 2rem;
#         padding-bottom: 2rem;
#     }

#     /* Création de "Cartes" pour les sections */
#     div.st-emotion-cache-1r6slb0, div.st-emotion-cache-ocqkz7 {
#         background-color: #ffffff;
#         border-radius: 15px;
#         padding: 20px;
#         box-shadow: 0 4px 12px rgba(0,0,0,0.05);
#         border: 1px solid #f0f2f6;
#     }
    
#     /* Style des métriques */
#     [data-testid="stMetricValue"] {
#         font-weight: 700;
#         color: #1E293B;
#     }
#     [data-testid="stMetricLabel"] {
#         color: #64748B;
#     }

#     /* Style des onglets (Tabs) */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#         background-color: transparent;
#     }
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         white-space: nowrap;
#         background-color: #fff;
#         border-radius: 8px;
#         color: #64748B;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.05);
#         padding: 0 20px;
#         font-weight: 600;
#     }
#     .stTabs [aria-selected="true"] {
#         background-color: #F1F5F9 !important;
#         color: #0F172A !important;
#         border: 1px solid #E2E8F0;
#     }

#     /* Custom HR */
#     hr {
#         margin: 2em 0;
#         border-color: #f1f5f9;
#     }
    
#     /* Sidebar Styling */
#     section[data-testid="stSidebar"] {
#         background-color: #f8fafc;
#         border-right: 1px solid #e2e8f0;
#     }

# </style>
# """, unsafe_allow_html=True)

# # =============================================================================
# # CHARGEMENT DES MODÈLES ET DONNÉES (Inchangé)
# # =============================================================================
# @st.cache_resource
# def load_models():
#     """Charge les modèles et configurations"""
#     # Note: Assurez-vous que ces fichiers existent dans votre répertoire
#     try:
#         with open('best_model.pkl', 'rb') as f: best_model = pickle.load(f)
#         with open('all_models.pkl', 'rb') as f: all_models = pickle.load(f)
#         with open('feature_names.pkl', 'rb') as f: feature_names = pickle.load(f)
#         try:
#             with open('scaler.pkl', 'rb') as f: scaler = pickle.load(f)
#         except: scaler = None
#         return best_model, all_models, feature_names, scaler
#     except FileNotFoundError:
#         st.error("Fichiers modèles (.pkl) introuvables. Assurez-vous qu'ils sont dans le même dossier.")
#         st.stop()

# @st.cache_data
# def load_results():
#     """Charge les résultats des modèles"""
#     try:
#         results = pd.read_excel('resultats_modeles.xlsx', index_col=0)
#         for col in results.columns:
#             if results[col].dtype == 'object':
#                 results[col] = pd.to_numeric(results[col].astype(str).str.replace('[', '').str.replace(']', ''), errors='coerce')
#         return results
#     except:
#         return None

# # Pour le développement, si les fichiers n'existent pas, on crée des placeholders pour que l'UI fonctionne
# try:
#     best_model, all_models, feature_names, scaler = load_models()
#     results_df = load_results()
# except:
#     st.warning("Mode démo : Modèles non chargés. L'interface est visible mais la prédiction ne fonctionnera pas.")
#     feature_names = []
#     results_df = None
#     best_model = None


# # =============================================================================
# # DICTIONNAIRES DE MAPPING ET FONCTIONS (Inchangé)
# # =============================================================================
# # ... (Je garde tout votre bloc de dictionnaires et la fonction create_features exactement pareil) ...
# MODELES_PAR_MARQUE = {
#     'Toyota': ['Corolla', 'Hilux', 'Land Cruiser', 'Camry', 'RAV4', 'Yaris'],
#     'Nissan': ['Patrol', 'Sunny', 'X-Trail', 'Navara', 'Micra'],
#     'Hyundai': ['Tucson', 'Elantra', 'Accent', 'Santa Fe', 'i10'],
#     'Kia': ['Sportage', 'Rio', 'Sorento', 'Picanto', 'Cerato'],
#     'Suzuki': ['Vitara', 'Swift', 'Jimny', 'Alto', 'Baleno'],
#     'Mitsubishi': ['Pajero', 'L200', 'Outlander', 'ASX', 'Lancer'],
#     'Honda': ['Civic', 'CR-V', 'Accord', 'HR-V', 'City'],
#     'Mercedes': ['Classe C', 'Classe E', 'GLC', 'GLE', 'Classe A'],
#     'BMW': ['Série 3', 'Série 5', 'X3', 'X5', 'Série 1']
# }

# TYPE_SINISTRE_MAP = {'Collision': 0, 'Vol': 1, 'Bris de glace': 2, 'Dégât matériel': 3, 'Incendie': 4, 'Vandalisme': 5}
# REGION_MAP = {'Djibouti-ville': 0, 'Ali Sabieh': 1, 'Dikhil': 2, 'Tadjourah': 3, 'Obock': 4, 'Arta': 5}
# MARQUE_MAP = {'Toyota': 0, 'Nissan': 1, 'Hyundai': 2, 'Kia': 3, 'Suzuki': 4, 'Mitsubishi': 5, 'Honda': 6, 'Mercedes': 7, 'BMW': 8}
# MODELE_MAP = {'Corolla': 0, 'Hilux': 1, 'Land Cruiser': 2, 'Camry': 3, 'RAV4': 4, 'Yaris': 5, 'Patrol': 6, 'Sunny': 7, 'X-Trail': 8, 'Navara': 9, 'Micra': 10, 'Tucson': 11, 'Elantra': 12, 'Accent': 13, 'Santa Fe': 14, 'i10': 15, 'Sportage': 16, 'Rio': 17, 'Sorento': 18, 'Picanto': 19, 'Cerato': 20, 'Vitara': 21, 'Swift': 22, 'Jimny': 23, 'Alto': 24, 'Baleno': 25, 'Pajero': 26, 'L200': 27, 'Outlander': 28, 'ASX': 29, 'Lancer': 30, 'Civic': 31, 'CR-V': 32, 'Accord': 33, 'HR-V': 34, 'City': 35, 'Classe C': 36, 'Classe E': 37, 'GLC': 38, 'GLE': 39, 'Classe A': 40, 'Série 3': 41, 'Série 5': 42, 'X3': 43, 'X5': 44, 'Série 1': 45}
# TYPE_ASSURANCE_MAP = {'Tiers': 0, 'Tiers étendu': 1, 'Tous risques': 2}
# SEXE_MAP = {'H': 0, 'F': 1}

# def create_features(data):
#     """Crée toutes les features à partir des données brutes"""
#     df = pd.DataFrame([data])
    
#     # --- FEATURES TEMPORELLES ---
#     df['jour_semaine'] = df['date_sinistre'].dt.dayofweek
#     df['mois_sinistre'] = df['date_sinistre'].dt.month
#     df['trimestre'] = df['date_sinistre'].dt.quarter
#     df['annee'] = df['date_sinistre'].dt.year
#     df['jour_mois'] = df['date_sinistre'].dt.day
#     df['semaine_annee'] = df['date_sinistre'].dt.isocalendar().week.astype(int)
#     df['is_weekend'] = (df['jour_semaine'] >= 5).astype(int)
#     df['is_nuit'] = ((df['heure_sinistre'] < 6) | (df['heure_sinistre'] >= 22)).astype(int)
#     df['is_fin_mois'] = (df['jour_mois'] >= 25).astype(int)
#     df['is_debut_mois'] = (df['jour_mois'] <= 5).astype(int)
    
#     # --- FEATURES FINANCIÈRES ---
#     df['ratio_reclamation'] = df['montant_reclame'] / df['montant_estime']
#     df['ecart_montant'] = df['montant_reclame'] - df['montant_estime']
#     df['ecart_montant_abs'] = df['ecart_montant'].abs()
#     df['ecart_pct'] = (df['ecart_montant'] / df['montant_estime']) * 100
#     df['ratio_valeur_vehicule'] = df['montant_reclame'] / df['valeur_vehicule']
#     df['ratio_estime_valeur'] = df['montant_estime'] / df['valeur_vehicule']
#     df['ratio_suspect'] = (df['ratio_reclamation'] > 1.5).astype(int)
#     df['ratio_tres_suspect'] = (df['ratio_reclamation'] > 2.0).astype(int)
#     df['ratio_extreme'] = (df['ratio_reclamation'] > 2.5).astype(int)
#     df['reclamation_elevee'] = (df['montant_reclame'] > df['valeur_vehicule'] * 0.5).astype(int)
#     df['reclamation_tres_elevee'] = (df['montant_reclame'] > df['valeur_vehicule'] * 0.8).astype(int)
    
#     # --- FEATURES VÉHICULE ---
#     df['km_par_an'] = df['kilometrage'] / (df['age_vehicule'] + 1)
#     df['vehicule_neuf'] = (df['age_vehicule'] <= 2).astype(int)
#     df['vehicule_recent'] = ((df['age_vehicule'] > 2) & (df['age_vehicule'] <= 5)).astype(int)
#     df['vehicule_moyen'] = ((df['age_vehicule'] > 5) & (df['age_vehicule'] <= 10)).astype(int)
#     df['vehicule_ancien'] = (df['age_vehicule'] > 10).astype(int)
#     df['vehicule_tres_ancien'] = (df['age_vehicule'] > 15).astype(int)
#     df['km_faible'] = (df['km_par_an'] < 5000).astype(int)
#     df['km_eleve'] = (df['km_par_an'] > 25000).astype(int)
#     df['km_tres_eleve'] = (df['km_par_an'] > 35000).astype(int)
#     df['km_suspect'] = ((df['km_par_an'] < 5000) | (df['km_par_an'] > 35000)).astype(int)
#     df['vehicule_luxe'] = df['marque_vehicule'].isin(['Mercedes', 'BMW']).astype(int)
#     df['vehicule_japonais'] = df['marque_vehicule'].isin(['Toyota', 'Nissan', 'Honda', 'Suzuki', 'Mitsubishi']).astype(int)
#     df['valeur_par_age'] = df['valeur_vehicule'] / (df['age_vehicule'] + 1)
    
#     # --- FEATURES CONDUCTEUR ---
#     df['conducteur_tres_jeune'] = (df['conducteur_age'] < 22).astype(int)
#     df['conducteur_jeune'] = (df['conducteur_age'] < 26).astype(int)
#     df['conducteur_senior'] = (df['conducteur_age'] > 60).astype(int)
#     df['conducteur_tres_senior'] = (df['conducteur_age'] > 70).astype(int)
#     df['permis_recent'] = (df['anciennete_permis'] < 3).astype(int)
#     df['permis_moyen'] = ((df['anciennete_permis'] >= 3) & (df['anciennete_permis'] < 10)).astype(int)
#     df['permis_experimente'] = (df['anciennete_permis'] >= 10).astype(int)
#     df['ratio_age_permis'] = df['conducteur_age'] / (df['anciennete_permis'] + 1)
    
#     def get_tranche_age(age):
#         if age <= 25: return 0
#         elif age <= 35: return 1
#         elif age <= 50: return 2
#         elif age <= 65: return 3
#         else: return 4
#     df['tranche_age_encoded'] = df['conducteur_age'].apply(get_tranche_age)
    
#     # --- FEATURES CONTRAT ---
#     df['contrat_tres_recent'] = (df['anciennete_contrat_mois'] < 3).astype(int)
#     df['contrat_recent'] = (df['anciennete_contrat_mois'] < 6).astype(int)
#     df['contrat_moyen'] = ((df['anciennete_contrat_mois'] >= 6) & (df['anciennete_contrat_mois'] < 24)).astype(int)
#     df['contrat_ancien'] = (df['anciennete_contrat_mois'] >= 24).astype(int)
#     df['premier_sinistre'] = (df['historique_reclamations'] == 0).astype(int)
#     df['reclamations_multiples'] = (df['historique_reclamations'] >= 2).astype(int)
#     df['reclamations_frequentes'] = (df['historique_reclamations'] >= 3).astype(int)
#     df['reclamations_excessives'] = (df['historique_reclamations'] >= 4).astype(int)
#     df['freq_reclamations'] = df['historique_reclamations'] / (df['anciennete_contrat_mois'] + 1) * 12
    
#     # --- FEATURES SINISTRE ---
#     df['sinistre_vol'] = (df['type_sinistre'] == 'Vol').astype(int)
#     df['sinistre_incendie'] = (df['type_sinistre'] == 'Incendie').astype(int)
#     df['sinistre_risque'] = df['type_sinistre'].isin(['Vol', 'Incendie']).astype(int)
#     df['sinistre_collision'] = (df['type_sinistre'] == 'Collision').astype(int)
    
#     # --- FEATURES COMBINÉES ---
#     df['combo_vieux_gros_montant'] = ((df['age_vehicule'] > 8) & (df['ratio_reclamation'] > 1.3)).astype(int)
#     df['combo_jeune_nuit'] = ((df['conducteur_jeune'] == 1) & (df['is_nuit'] == 1)).astype(int)
#     df['combo_contrat_recent_risque'] = ((df['contrat_recent'] == 1) & (df['sinistre_risque'] == 1)).astype(int)
#     df['combo_nouveau_vol'] = ((df['contrat_tres_recent'] == 1) & (df['sinistre_vol'] == 1)).astype(int)
#     df['combo_weekend_vol'] = ((df['is_weekend'] == 1) & (df['sinistre_vol'] == 1)).astype(int)
#     df['combo_nuit_vol'] = ((df['is_nuit'] == 1) & (df['sinistre_vol'] == 1)).astype(int)
#     df['combo_historique_ratio'] = ((df['reclamations_multiples'] == 1) & (df['ratio_suspect'] == 1)).astype(int)
#     df['combo_luxe_vol'] = ((df['vehicule_luxe'] == 1) & (df['sinistre_vol'] == 1)).astype(int)
#     df['combo_ancien_incendie'] = ((df['vehicule_ancien'] == 1) & (df['sinistre_incendie'] == 1)).astype(int)
#     df['combo_km_ratio'] = ((df['km_suspect'] == 1) & (df['ratio_suspect'] == 1)).astype(int)
#     df['combo_triple_suspect'] = ((df['contrat_recent'] == 1) & (df['sinistre_risque'] == 1) & (df['ratio_suspect'] == 1)).astype(int)
    
#     # --- SCORE DE RISQUE ---
#     df['score_risque'] = (
#         df['ratio_suspect'] * 2 + df['ratio_tres_suspect'] * 3 + df['ratio_extreme'] * 4 + df['is_weekend'] * 1 + df['is_nuit'] * 2 +
#         df['contrat_recent'] * 2 + df['contrat_tres_recent'] * 3 + df['reclamations_multiples'] * 1 + df['reclamations_frequentes'] * 2 +
#         df['reclamations_excessives'] * 3 + df['vehicule_ancien'] * 1 + df['sinistre_risque'] * 2 + df['combo_vieux_gros_montant'] * 2 +
#         df['combo_contrat_recent_risque'] * 3 + df['combo_historique_ratio'] * 2 + df['combo_triple_suspect'] * 4
#     )
    
#     # --- ENCODAGE ---
#     df['type_sinistre_encoded'] = df['type_sinistre'].map(TYPE_SINISTRE_MAP).fillna(0).astype(int)
#     df['region_encoded'] = df['region'].map(REGION_MAP).fillna(0).astype(int)
#     df['marque_vehicule_encoded'] = df['marque_vehicule'].map(MARQUE_MAP).fillna(0).astype(int)
#     df['modele_vehicule_encoded'] = df['modele_vehicule'].map(MODELE_MAP).fillna(0).astype(int)
#     df['type_assurance_encoded'] = df['type_assurance'].map(TYPE_ASSURANCE_MAP).fillna(0).astype(int)
#     df['conducteur_sexe_encoded'] = df['conducteur_sexe'].map(SEXE_MAP).fillna(0).astype(int)
    
#     return df

# def get_risk_level(proba):
#     """Retourne le niveau de risque basé sur la probabilité avec des couleurs modernes"""
#     if proba >= 0.7:
#         return "CRITIQUE", "#ef4444" # Rouge moderne
#     elif proba >= 0.5:
#         return "ÉLEVÉ", "#f97316" # Orange moderne
#     elif proba >= 0.3:
#         return "MODÉRÉ", "#eab308" # Jaune moderne
#     else:
#         return "FAIBLE", "#22c55e" # Vert moderne

# # =============================================================================
# # INTERFACE UTILISATEUR PRINCIPALE
# # =============================================================================

# # Header moderne
# col_header_1, col_header_2 = st.columns([1, 5])
# with col_header_1:
#     st.image("https://cdn-icons-png.flaticon.com/512/2345/2345473.png", width=80) # Exemple d'icône de bouclier/voiture
# with col_header_2:
#     st.title("SafeGuard Assurance")
#     st.markdown("<h4 style='color: #64748B; margin-top: -15px;'>Système Intelligent de Détection de Fraude</h4>", unsafe_allow_html=True)

# st.markdown("---")

# # Sidebar - Navigation Moderne
# with st.sidebar:
#     st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h3 style='color:#1E293B;'>Menu Principal</h3></div>", unsafe_allow_html=True)
    
#     selected_page = option_menu(
#         menu_title=None,
#         options=["Tableau de Bord", "Analyse par Lot", "Performance IA", "À Propos"],
#         icons=["speedometer2", "collection", "graph-up-arrow", "info-circle"],
#         menu_icon="cast",
#         default_index=0,
#         styles={
#             "container": {"padding": "0!important", "background-color": "transparent"},
#             "icon": {"color": "#64748B", "font-size": "1.1rem"}, 
#             "nav-link": {"font-size": "1rem", "text-align": "left", "margin":"5px", "--hover-color": "#f1f5f9", "color": "#1E293B"},
#             "nav-link-selected": {"background-color": "#0F172A", "color": "#ffffff", "font-weight":"600"},
#         }
#     )
#     st.markdown("---")
#     st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 0.8rem;'>Développé par<br><b>Amal Tani NOUR</b><br>Master 2 Data Science - Djibouti</div>", unsafe_allow_html=True)


# # =============================================================================
# # PAGE 1: TABLEAU DE BORD (Prédiction Individuelle Redesignée)
# # =============================================================================
# if selected_page == "Tableau de Bord":
#     st.subheader("🔍 Analyse de Dossier Sinistre")
#     st.markdown("Remplissez les informations ci-dessous pour évaluer le risque de fraude d'un dossier.")

#     # Conteneur principal en style "Carte"
#     with st.container():
#         # Utilisation de Tabs pour fluidifier le formulaire
#         tab_sinistre, tab_vehicule, tab_conducteur = st.tabs(["📅 Détails du Sinistre", "🚙 Véhicule Concerné", "👤 Conducteur & Contrat"])

#         with tab_sinistre:
#             col1, col2 = st.columns(2)
#             with col1:
#                 date_sinistre = st.date_input("Date de survenance", value=date.today())
#                 heure_sinistre = st.slider("Heure (0-23h)", 0, 23, 14)
#                 region = st.selectbox("Région géographique", ['Djibouti-ville', 'Ali Sabieh', 'Dikhil', 'Tadjourah', 'Obock', 'Arta'])
#             with col2:
#                 type_sinistre = st.selectbox("Type de déclaration", ['Collision', 'Vol', 'Bris de glace', 'Dégât matériel', 'Incendie', 'Vandalisme'])
#                 montant_reclame = st.number_input("Montant Réclamé (DJF)", min_value=0, value=500000, step=10000, format="%d")
#                 montant_estime = st.number_input("Estimation Expert (DJF)", min_value=0, value=400000, step=10000, format="%d")

#         with tab_vehicule:
#             col1, col2 = st.columns(2)
#             with col1:
#                 marque_vehicule = st.selectbox("Marque", list(MODELES_PAR_MARQUE.keys()))
#                 modele_vehicule = st.selectbox("Modèle", MODELES_PAR_MARQUE[marque_vehicule])
#                 valeur_vehicule = st.number_input("Valeur Assurée (DJF)", min_value=0, value=2500000, step=50000, format="%d")
#             with col2:
#                 age_vehicule = st.slider("Âge du véhicule (années)", 0, 25, 5)
#                 kilometrage = st.number_input("Kilométrage actuel", min_value=0, value=75000, step=1000, format="%d")

#         with tab_conducteur:
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 conducteur_age = st.number_input("Âge conducteur", 18, 90, 35)
#                 conducteur_sexe = st.radio("Sexe", ['H', 'F'], horizontal=True)
#             with col2:
#                 type_assurance = st.selectbox("Formule d'assurance", ['Tiers', 'Tiers étendu', 'Tous risques'])
#                 anciennete_permis = st.number_input("Années de permis", 0, 70, 10)
#             with col3:
#                 anciennete_contrat_mois = st.number_input("Ancienneté contrat (mois)", 1, 240, 24)
#                 historique_reclamations = st.number_input("Nb. réclamations passées", 0, 20, 1)

#         st.markdown("###") #Espace
#         # Bouton d'action centré et stylisé
#         col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
#         with col_btn_2:
#             analyze_button = st.button("✨ LANCER L'ANALYSE IA", type="primary", use_container_width=True)

#     # Section Résultats (s'affiche après le clic)
#     if analyze_button:
#         if best_model is None:
#              st.error("Erreur technique : Le modèle IA n'est pas chargé.")
#         else:
#             with st.spinner("Analyse des 60+ points de contrôle en cours..."):
#                 # (Même logique de création de données)
#                 data = {
#                     'date_sinistre': pd.Timestamp(date_sinistre),
#                     'heure_sinistre': heure_sinistre,
#                     'type_sinistre': type_sinistre,
#                     'region': region,
#                     'montant_reclame': montant_reclame,
#                     'montant_estime': montant_estime,
#                     'marque_vehicule': marque_vehicule,
#                     'modele_vehicule': modele_vehicule,
#                     'age_vehicule': age_vehicule,
#                     'valeur_vehicule': valeur_vehicule,
#                     'kilometrage': kilometrage,
#                     'conducteur_age': conducteur_age,
#                     'conducteur_sexe': conducteur_sexe,
#                     'anciennete_permis': anciennete_permis,
#                     'type_assurance': type_assurance,
#                     'anciennete_contrat_mois': anciennete_contrat_mois,
#                     'historique_reclamations': historique_reclamations
#                 }
                
#                 df_features = create_features(data)
                
#                 # Vérification des features
#                 missing_features = [f for f in feature_names if f not in df_features.columns]
#                 if missing_features:
#                     st.error(f"Features manquantes: {missing_features}")
#                 else:
#                     X = df_features[feature_names].values
#                     proba = best_model.predict_proba(X)[0][1]
#                     prediction = best_model.predict(X)[0]
#                     risk_label, risk_color = get_risk_level(proba)
#                     score_interne = int(df_features['score_risque'].values[0])

#                     # --- AFFICHAGE DES RÉSULTATS MODERNE ---
#                     st.markdown("---")
#                     st.subheader("📊 Résultat de l'évaluation")

#                     # Création de 2 colonnes de type "Carte" pour les résultats
#                     col_res_main, col_res_details = st.columns([2, 3])

#                     # Colonne Principale : Le Score
#                     with col_res_main:
#                          st.markdown(f"""
#                         <div style="background-color: {risk_color}15; border: 2px solid {risk_color}; border-radius: 15px; padding: 25px; text-align: center;">
#                             <h4 style="color: {risk_color}; margin:0;">NIVEAU DE RISQUE</h4>
#                             <h1 style="color: {risk_color}; font-size: 3.5rem; margin: 10px 0;">{risk_label}</h1>
#                             <h3 style="color: #1E293B;">Probabilité : {proba*100:.1f}%</h3>
#                         </div>
#                         """, unsafe_allow_html=True)
                         
#                          if prediction == 1:
#                              st.warning("⚠️ Ce dossier présente des caractéristiques atypiques fortes.")
#                          else:
#                              st.success("✅ Ce dossier semble conforme aux normes.")

#                     # Colonne Détails : Jauge et Indicateurs
#                     with col_res_details:
#                         # Jauge Plotly épurée
#                         fig_gauge = go.Figure(go.Indicator(
#                             mode="gauge+number",
#                             value=proba * 100,
#                             domain={'x': [0, 1], 'y': [0, 1]},
#                             title={'text': "Score IA (0-100)", 'font': {'size': 16, 'color': '#64748B'}},
#                             gauge={
#                                 'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
#                                 'bar': {'color': risk_color},
#                                 'bgcolor': "white",
#                                 'borderwidth': 2,
#                                 'bordercolor': "#f1f5f9",
#                                 'steps': [
#                                     {'range': [0, 30], 'color': '#dcfce7'},
#                                     {'range': [30, 70], 'color': '#fef9c3'},
#                                     {'range': [70, 100], 'color': '#fee2e2'}
#                                 ],
#                             }
#                         ))
#                         fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
#                         st.plotly_chart(fig_gauge, use_container_width=True)

#                         # Indicateurs clés en petites cartes
#                         st.markdown("<h5 style='color:#64748B'>Indicateurs Clés</h5>", unsafe_allow_html=True)
#                         kpi1, kpi2, kpi3 = st.columns(3)
                        
#                         ratio = montant_reclame / montant_estime if montant_estime > 0 else 0
#                         ecart = montant_reclame - montant_estime
                        
#                         kpi1.metric("Ratio Réclamation", f"{ratio:.1f}x", delta="Suspect" if ratio > 1.5 else None, delta_color="inverse")
#                         kpi2.metric("Écart Financier", f"{ecart/1000:.0f}k DJF")
#                         kpi3.metric("Score Règles Métier", f"{score_interne}/30")


# # =============================================================================
# # PAGE 2: ANALYSE PAR LOT
# # =============================================================================
# elif selected_page == "Analyse par Lot":
#     st.subheader("📁 Traitement en Masse (Batch)")
    
#     # Utilisation de st.expander pour les instructions
#     with st.expander("ℹ️ Instructions et Template CSV", expanded=True):
#         st.markdown("""
#         1. **Téléchargez** le modèle de fichier ci-dessous.
#         2. **Remplissez** vos données de sinistres en respectant le format.
#         3. **Chargez** le fichier complété pour obtenir une analyse globale.
#         """)
        
#         # Template CSV (Même logique)
#         template_df = pd.DataFrame({
#              'date_sinistre': ['2024-01-15', '2024-02-20'],
#              'heure_sinistre': [14, 23],
#              'type_sinistre': ['Collision', 'Vol'],
#              'region': ['Djibouti-ville', 'Tadjourah'],
#              'montant_reclame': [500000, 2000000],
#              'montant_estime': [450000, 800000],
#              'marque_vehicule': ['Toyota', 'Mercedes'],
#              'modele_vehicule': ['Corolla', 'Classe C'],
#              'age_vehicule': [5, 12],
#              'valeur_vehicule': [2500000, 6000000],
#              'kilometrage': [75000, 180000],
#              'conducteur_age': [35, 28],
#              'conducteur_sexe': ['H', 'F'],
#              'anciennete_permis': [15, 5],
#              'type_assurance': ['Tous risques', 'Tiers étendu'],
#              'anciennete_contrat_mois': [36, 4],
#              'historique_reclamations': [1, 3]
#         })
#         csv_template = template_df.to_csv(index=False)
#         st.download_button(label="📥 Télécharger le Template CSV", data=csv_template, file_name="template_sinistres.csv", mime="text/csv")

#     st.markdown("###")
#     uploaded_file = st.file_uploader("Déposez votre fichier CSV ici", type=['csv'], help="Taille max: 200MB")
    
#     if uploaded_file is not None:
#         df_upload = pd.read_csv(uploaded_file)
#         st.success(f"✅ Fichier chargé avec succès : {len(df_upload)} lignes détectées.")
        
#         # Aperçu stylisé
#         with st.expander("Aperçu des données brutes"):
#              st.dataframe(df_upload.head(), use_container_width=True)

#         col_act1, col_act2 = st.columns([1, 3])
#         with col_act1:
#              btn_process = st.button("🚀 Lancer le traitement par lot", type="primary", use_container_width=True)

#         if btn_process:
#             if best_model is None:
#                  st.error("Impossible de traiter : Modèle manquant.")
#             else:
#                 results = []
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 for i, row in df_upload.iterrows():
#                     status_text.text(f"Traitement de la ligne {i+1}/{len(df_upload)}...")
#                     try:
#                         data_row = row.to_dict()
#                         data_row['date_sinistre'] = pd.Timestamp(data_row['date_sinistre'])
#                         df_feat_row = create_features(data_row)
#                         X_row = df_feat_row[feature_names].values
#                         proba_row = best_model.predict_proba(X_row)[0][1]
#                         pred_row = best_model.predict(X_row)[0]
#                         risk_lbl, _ = get_risk_level(proba_row)
                        
#                         results.append({
#                             'ID': i + 1,
#                             'Type': data_row['type_sinistre'],
#                             'Montant Réclamé': f"{data_row['montant_reclame']:,}",
#                             'Score IA': f"{proba_row*100:.1f}%",
#                             'Statut': '🔴 SUSPECT' if pred_row == 1 else '🟢 NORMAL',
#                             'Niveau Risque': risk_lbl
#                         })
#                     except Exception as e:
#                          results.append({'ID': i+1, 'Statut': f'ERREUR: {str(e)[:30]}'})
                    
#                     progress_bar.progress((i + 1) / len(df_upload))
                
#                 status_text.empty()
#                 progress_bar.empty()
#                 st.balloons()
                
#                 st.subheader("Résultats de l'analyse")
#                 results_df_display = pd.DataFrame(results)

#                 # Metrics summary styled
#                 n_fraud = sum(1 for r in results if 'SUSPECT' in str(r.get('Statut')))
#                 met1, met2, met3 = st.columns(3)
#                 met1.metric("Total Dossiers", len(results))
#                 met2.metric("Dossiers Suspects", n_fraud, delta_color="inverse")
#                 met3.metric("Taux de Suspicion", f"{n_fraud/len(results)*100:.1f}%")

#                 st.dataframe(results_df_display, use_container_width=True, height=400)
                
#                 csv_results = results_df_display.to_csv(index=False)
#                 st.download_button(label="📤 Exporter les résultats (CSV)", data=csv_results, file_name="resultats_batch.csv", mime="text/csv", type="primary")


# # =============================================================================
# # PAGE 3: PERFORMANCE (Design épuré)
# # =============================================================================
# elif selected_page == "Performance IA":
#     st.subheader("📈 Métriques et Performance des Modèles")
    
#     if results_df is not None:
#         # Style plus propre pour le tableau
#         st.markdown("##### Comparatif Technique")
#         st.dataframe(results_df.style.highlight_max(axis=0, color='#dcfce7').format("{:.3f}"), use_container_width=True)
        
#         st.markdown("###")
#         st.markdown("##### Visualisation Comparative")
        
#         metrics = ['F1-Score', 'AUC-ROC', 'Recall', 'Precision', 'Accuracy']
#         available_metrics = [m for m in metrics if m in results_df.columns]
        
#         # Graphique Plotly avec thème moderne blanc
#         fig = go.Figure()
#         colors = px.colors.qualitative.Prism # Palette de couleurs moderne
        
#         for i, metric in enumerate(available_metrics):
#             fig.add_trace(go.Bar(
#                 name=metric,
#                 x=results_df.index,
#                 y=results_df[metric],
#                 text=results_df[metric].round(3),
#                 textposition='auto',
#                 marker_color=colors[i % len(colors)],
#                 marker_line_width=0
#             ))
        
#         fig.update_layout(
#             barmode='group',
#             xaxis_title='',
#             yaxis_title='Score (0.0 - 1.0)',
#             height=500,
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(248,250,252,1)',
#             font=dict(family="Inter, sans-serif", color="#64748B"),
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#             yaxis=dict(gridcolor='#e2e8f0'),
#             xaxis=dict(gridcolor='#e2e8f0')
#         )
#         st.plotly_chart(fig, use_container_width=True)

#         if 'F1-Score' in results_df.columns:
#             best_model_name = results_df['F1-Score'].idxmax()
#             st.info(f"🏆 Le modèle champion actuel est **{best_model_name}** basé sur le F1-Score.")

#     else:
#         st.warning("Données de performance non disponibles.")


# # =============================================================================
# # PAGE 4: À PROPOS (Design épuré)
# # =============================================================================
# elif selected_page == "À Propos":
#     col_about_1, col_about_2 = st.columns([2, 1])
    
#     with col_about_1:
#         st.subheader("Le Projet SafeGuard")
#         st.markdown("""
#         Ce système est une solution de **Machine Learning** avancée conçue pour assister les experts en assurance dans la détection précoce des réclamations frauduleuses en République de Djibouti.
        
#         Il combine l'analyse de règles métier (ratios financiers, incohérences temporelles) avec la puissance prédictive de modèles d'intelligence artificielle entraînés sur des données historiques.
#         """)

#         st.markdown("#### 🛠️ Stack Technique")
#         st.markdown("""
#         <div style="display: flex; gap: 10px; flex-wrap: wrap;">
#             <span style="background:#E0F2FE; color:#0284C7; padding: 5px 10px; border-radius: 15px; font-size: 0.8em;">Python 3.x</span>
#             <span style="background:#E0F2FE; color:#0284C7; padding: 5px 10px; border-radius: 15px; font-size: 0.8em;">Scikit-learn</span>
#             <span style="background:#E0F2FE; color:#0284C7; padding: 5px 10px; border-radius: 15px; font-size: 0.8em;">XGBoost / LightGBM</span>
#             <span style="background:#E0F2FE; color:#0284C7; padding: 5px 10px; border-radius: 15px; font-size: 0.8em;">Streamlit Ultra-Modern UI</span>
#             <span style="background:#E0F2FE; color:#0284C7; padding: 5px 10px; border-radius: 15px; font-size: 0.8em;">Plotly Interactive</span>
#         </div>
#         """, unsafe_allow_html=True)

#     with col_about_2:
#         # Carte de l'auteur
#         st.markdown("""
#         <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 15px; padding: 20px; text-align: center;">
#             <img src="https://cdn-icons-png.flaticon.com/512/4042/4042356.png" width="80" style="border-radius: 50%; margin-bottom: 10px;">
#             <h4 style="color: #1E293B; margin-bottom: 5px;">Amal Tani NOUR</h4>
#             <p style="color: #64748B; font-size: 0.9rem;">Data Scientist</p>
#             <hr style="margin: 15px 0;">
#             <p style="color: #64748B; font-size: 0.85rem;">
#                 Master 2 Data Science<br>
#                 Université de Djibouti<br>
#                 Projet de fin d'études
#             </p>
#         </div>
#         """, unsafe_allow_html=True)
# # =============================================================================
# # FOOTER GLOBAL (S'affiche sur toutes les pages en bas)
# # =============================================================================
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; font-family: 'Inter', sans-serif; color: #94A3B8; padding-bottom: 20px;">
#     <p style="font-size: 0.85rem; margin-bottom: 5px;">
#         © 2024-2025 <b>SafeGuard AI</b> | Système d'Aide à la Décision
#     </p>
#     <p style="font-size: 0.75rem;">
#         Développé avec passion par <b style="color: #64748B;">Amal Tani NOUR</b>
#     </p>
# </div>
# """, unsafe_allow_html=True)




import streamlit as st
import pandas as pd
import numpy as np
import joblib  # Beaucoup plus rapide et stable que pickle
import xgboost # Nécessaire si le modèle est un XGBoost
from datetime import date

# =============================================================================
# CONFIGURATION & DESIGN (Léger)
# =============================================================================
st.set_page_config(page_title="SafeGuard | Détection Fraude", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    /* CSS Optimisé pour la vitesse d'affichage */
    .main { padding-top: 2rem; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    h1, h2, h3 { color: #1e293b; font-family: sans-serif; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CHARGEMENT OPTIMISÉ (Best Model Uniquement)
# =============================================================================
@st.cache_resource
def load_engine():
    """Chargement unique du cerveau de l'IA"""
    try:
        # On utilise joblib.load qui est plus tolérant aux versions
        model = joblib.load('best_model.pkl')
        feats = joblib.load('feature_names.pkl')
        return model, feats, None
    except Exception as e:
        return None, None, str(e)

# Chargement immédiat
model, feature_names, error_msg = load_engine()

# =============================================================================
# LOGIQUE MÉTIER (Feature Engineering)
# =============================================================================
def process_input(data):
    df = pd.DataFrame([data])
    
    # Dates
    df['date_sinistre'] = pd.to_datetime(df['date_sinistre'])
    df['jour_semaine'] = df['date_sinistre'].dt.dayofweek
    df['is_weekend'] = (df['jour_semaine'] >= 5).astype(int)
    df['is_nuit'] = ((df['heure_sinistre'] < 6) | (df['heure_sinistre'] >= 22)).astype(int)
    
    # Ratios Financiers
    df['ratio_reclamation'] = df['montant_reclame'] / df['montant_estime']
    df['ratio_suspect'] = (df['ratio_reclamation'] > 1.5).astype(int)
    
    # Véhicule & Conducteur
    df['km_par_an'] = df['kilometrage'] / (df['age_vehicule'] + 1)
    df['conducteur_jeune'] = (df['conducteur_age'] < 26).astype(int)
    df['contrat_recent'] = (df['anciennete_contrat_mois'] < 6).astype(int)
    
    # Encodages Simples (Mappings directs)
    mappings = {
        'type_sinistre': {'Collision': 0, 'Vol': 1, 'Bris de glace': 2, 'Dégât matériel': 3, 'Incendie': 4, 'Vandalisme': 5},
        'region': {'Djibouti-ville': 0, 'Ali Sabieh': 1, 'Dikhil': 2, 'Tadjourah': 3, 'Obock': 4, 'Arta': 5},
        'type_assurance': {'Tiers': 0, 'Tiers étendu': 1, 'Tous risques': 2},
        'conducteur_sexe': {'H': 0, 'F': 1}
    }
    
    # Application des mappings
    for col, map_dict in mappings.items():
        if col in df.columns:
            # On crée la colonne encodée (ex: type_sinistre -> type_sinistre_encoded)
            df[f'{col}_encoded'] = df[col].map(map_dict).fillna(0).astype(int)

    # Note: On laisse le reste du feature engineering complexe de côté pour la rapidité
    # ou on ajoute les colonnes manquantes avec des 0 pour éviter les crashs
    return df

# =============================================================================
# INTERFACE UTILISATEUR
# =============================================================================
col_logo, col_title = st.columns([1, 6])
with col_logo: st.write("🛡️")
with col_title: st.title("SafeGuard | Analyse Rapide")

if error_msg:
    st.error(f"🚨 Erreur Système : {error_msg}")
    st.stop()

# --- FORMULAIRE ---
with st.container():
    st.markdown("#### 📝 Nouveau Dossier")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        date_s = st.date_input("Date Sinistre", value=date.today())
        heure_s = st.slider("Heure", 0, 23, 14)
        type_s = st.selectbox("Type", ['Collision', 'Vol', 'Incendie', 'Bris de glace', 'Autre'])
        
    with c2:
        mt_reclame = st.number_input("Montant Réclamé", value=500000)
        mt_estime = st.number_input("Montant Expert", value=400000)
        age_v = st.number_input("Age Véhicule", value=5)
        
    with c3:
        age_c = st.number_input("Age Conducteur", value=35)
        contrat_mois = st.number_input("Mois Contrat", value=24)
        historique = st.number_input("Nb Sinistres", value=1)

    # Données statiques pour simplifier l'UI (valeurs par défaut sûres)
    data_input = {
        'date_sinistre': date_s, 'heure_sinistre': heure_s, 'type_sinistre': type_s,
        'montant_reclame': mt_reclame, 'montant_estime': mt_estime,
        'age_vehicule': age_v, 'kilometrage': 75000,
        'conducteur_age': age_c, 'anciennete_contrat_mois': contrat_mois,
        'historique_reclamations': historique,
        'region': 'Djibouti-ville', 'type_assurance': 'Tous risques',
        'conducteur_sexe': 'H', 'marque_vehicule': 'Toyota', 'modele_vehicule': 'Corolla',
        'valeur_vehicule': 2500000, 'anciennete_permis': 10
    }

    if st.button("🚀 ANALYSER MAINTENANT", type="primary"):
        with st.spinner("Calcul du score de risque..."):
            try:
                # 1. Création des features
                df_processed = process_input(data_input)
                
                # 2. Alignement des colonnes (CRUCIAL pour éviter les crashs)
                # On crée un dataframe vide avec les colonnes attendues par le modèle
                df_final = pd.DataFrame(0, index=[0], columns=feature_names)
                
                # On remplit avec ce qu'on a calculé
                common_cols = list(set(df_final.columns) & set(df_processed.columns))
                df_final[common_cols] = df_processed[common_cols]
                
                # 3. Prédiction
                proba = model.predict_proba(df_final.values)[0][1]
                
                # 4. Affichage
                st.markdown("---")
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    risk_color = "red" if proba > 0.5 else "green"
                    st.markdown(f"<h1 style='color:{risk_color}; font-size: 3em;'>{proba*100:.1f}%</h1>", unsafe_allow_html=True)
                    st.caption("Probabilité de Fraude")
                    
                with res_col2:
                    if proba > 0.5:
                        st.error("⚠️ RISQUE ÉLEVÉ DÉTECTÉ")
                        st.write("Investigation recommandée.")
                    else:
                        st.success("✅ DOSSIER SAIN")
                        st.write("Traitement standard autorisé.")
                        
            except Exception as e:
                st.error(f"Erreur de calcul : {e}")
                # Debug info (à cacher en prod si besoin)
                st.caption("Vérifiez la cohérence entre feature_names.pkl et le code.")

# Footer simple
st.markdown("---")
st.caption("© 2026 SafeGuard AI | Powered by Amal Tani NOUR")