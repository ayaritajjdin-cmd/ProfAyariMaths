import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# --- CONFIGURATION ---
MOT_DE_PASSE_ADMIN = "prof2025"
FICHIER_SCORES = "scores_classe.csv"

# --- GESTION DE LA BASE DE DONNÉES (FICHIER CSV PARTAGÉ) ---
def init_db():
    if not os.path.exists(FICHIER_SCORES):
        # On crée un fichier vide avec les colonnes
        df = pd.DataFrame(columns=["Date", "Nom", "Score"])
        df.to_csv(FICHIER_SCORES, index=False)

def lire_scores():
    init_db()
    try:
        return pd.read_csv(FICHIER_SCORES)
    except:
        return pd.DataFrame(columns=["Date", "Nom", "Score"])

def sauvegarder_score(nom, score):
    init_db()
    df = pd.read_csv(FICHIER_SCORES)
    # Ajout du nouveau score
    nouveau = pd.DataFrame({
        "Date": [datetime.now().strftime("%d/%m %H:%M")],
        "Nom": [nom],
        "Score": [score]
    })
    df = pd.concat([df, nouveau], ignore_index=True)
    df.to_csv(FICHIER_SCORES, index=False)

def tout_effacer():
    if os.path.exists(FICHIER_SCORES):
        os.remove(FICHIER_SCORES)
        init_db()

# --- JEU MATHS ---
def generer_question():
    ops = ['+', '-', '*', '/']
    op = random.choice(ops)
    a, b = random.randint(2, 20), random.randint(2, 20)
    
    if op == '+': txt, rep = f"{a} + {b}", a + b
    elif op == '-': 
        if a < b: a, b = b, a
        txt, rep = f"{a} - {b}", a - b
    elif op == '*': 
        a, b = random.randint(2, 12), random.randint(2, 10)
        txt, rep = f"{a} x {b}", a * b
    else: 
        b = random.randint(2, 10); res = random.randint(2, 10)
        a = b * res
        txt, rep = f"{a} ÷ {b}", res
    return txt, rep

# --- INTERFACE WEB ---
st.set_page_config(page_title="Maths Élites", page_icon="🎓")

# Mémoire du jeu
if 'score' not in st.session_state: st.session_state.score = 0
if 'q' not in st.session_state: st.session_state.q, st.session_state.r = generer_question()
if 'msg' not in st.session_state: st.session_state.msg = ""

# --- VOLET ADMIN (Barre latérale gauche) ---
with st.sidebar:
    st.header("🔒 Espace Professeur")
    pwd = st.text_input("Mot de passe :", type="password")
    
    if pwd == MOT_DE_PASSE_ADMIN:
        st.success("Admin Connecté")
        st.write("---")
        st.subheader("📋 Historique Complet des Élèves")
        
        df_admin = lire_scores()
        # Affiche le tableau complet (Date, Nom, Score)
        st.dataframe(df_admin, use_container_width=True)
        
        # Bouton pour télécharger en Excel/CSV
        csv = df_admin.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, "scores_eleves.csv", "text/csv")
        
        st.write("---")
        if st.button("🗑️ EFFACER TOUT L'HISTORIQUE", type="primary"):
            tout_effacer()
            st.warning("Historique supprimé !")
            st.rerun()

# --- PAGE PRINCIPALE ---
st.title("🎓 DÉFI MATHS - Prof. Ayari")

nom = st.text_input("Entre ton Prénom pour jouer :")

if nom:
    tab1, tab2 = st.tabs(["🎮 JOUER", "🏆 CLASSEMENT DE LA CLASSE"])

    # ONGLET 1 : LE JEU
    with tab1:
        st.write("---")
        col1, col2 = st.columns(2)
        col1.metric("Score Actuel", st.session_state.score)
        
        st.header(f"Calcul : {st.session_state.q} = ?")
        
        with st.form("jeu"):
            rep_eleve = st.number_input("Réponse :", step=1)
            if st.form_submit_button("Valider"):
                if rep_eleve == st.session_state.r:
                    st.session_state.score += 1
                    st.session_state.msg = "✅ BRAVO !"
                    # SAUVEGARDE AUTOMATIQUE DU SCORE DANS L'HISTORIQUE COMMUN
                    sauvegarder_score(nom, st.session_state.score)
                else:
                    st.session_state.msg = f"❌ FAUX ! C'était {st.session_state.r}"
                
                st.session_state.q, st.session_state.r = generer_question()
                st.rerun()

        if st.session_state.msg: st.info(st.session_state.msg)

    # ONGLET 2 : CLASSEMENT PUBLIC
    with tab2:
        st.subheader("🏆 Les Champions de la Classe")
        df_public = lire_scores()
        
        if not df_public.empty:
            # On prend le MEILLEUR score de chaque élève pour le classement
            classement = df_public.groupby("Nom")["Score"].max().reset_index()
            # On trie du plus grand au plus petit
            classement = classement.sort_values(by="Score", ascending=False).head(15)
            # On affiche (sans la date, juste Nom et Score)
            classement.index = range(1, len(classement) + 1)
            st.table(classement)
        else:
            st.info("Aucun match joué pour l'instant.")

else:
    st.info("👋 Écris ton prénom ci-dessus pour commencer.")
