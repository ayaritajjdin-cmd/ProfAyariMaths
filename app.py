import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# --- CONFIGURATION ---
MOT_DE_PASSE_ADMIN = "prof2025"
FICHIER_SCORES = "scores_classe.csv"
VIES_INITIALES = 5 # NOUVELLE RÈGLE : 5 chances pour faire le meilleur score

# --- GESTION DE LA BASE DE DONNÉES (FICHIER CSV PARTAGÉ) ---
def init_db():
    if not os.path.exists(FICHIER_SCORES):
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

# --- FONCTION DE REDÉMARRAGE DU JEU ---
def redemarrer_jeu(nom_joueur):
    st.session_state.score = 0
    st.session_state.vies = VIES_INITIALES
    st.session_state.partie_en_cours = True
    st.session_state.q, st.session_state.r = generer_question()
    st.session_state.msg = f"Bonne chance, {nom_joueur} !"
    st.rerun()

# --- INTERFACE WEB ---
st.set_page_config(page_title="Maths Élites", page_icon="🎓")

# Initialisation de la mémoire du jeu
if 'score' not in st.session_state: st.session_state.score = 0
if 'vies' not in st.session_state: st.session_state.vies = VIES_INITIALES
if 'q' not in st.session_state: st.session_state.q, st.session_state.r = generer_question()
if 'msg' not in st.session_state: st.session_state.msg = "Entrez votre prénom pour commencer."
if 'partie_en_cours' not in st.session_state: st.session_state.partie_en_cours = False


# --- VOLET ADMIN (Barre latérale gauche) ---
with st.sidebar:
    st.header("🔒 Espace Professeur")
    pwd = st.text_input("Mot de passe :", type="password")
    
    if pwd == MOT_DE_PASSE_ADMIN:
        st.success("Admin Connecté")
        st.write("---")
        st.subheader("📋 Historique Complet")
        
        df_admin = lire_scores()
        st.dataframe(df_admin, use_container_width=True)
        
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
    # Si la partie n'a pas commencé, affiche le bouton de démarrage
    if not st.session_state.partie_en_cours:
        st.info(f"Bonjour {nom} ! Tu as {VIES_INITIALES} vies. Fais le meilleur score possible !")
        if st.button("Démarrer le Défi"):
            redemarrer_jeu(nom)
            
    # Si la partie est terminée (0 vie)
    elif st.session_state.vies <= 0:
        st.error(f"Partie Terminée ! Ton score final est : {st.session_state.score}")
        st.session_state.partie_en_cours = False
        
        if st.button("Rejouer"):
            redemarrer_jeu(nom)

    # Si la partie est en cours
    else:
        tab1, tab2 = st.tabs(["🎮 JEU ACTUEL", "🏆 CLASSEMENT"])

        with tab1:
            st.write("---")
            col1, col2 = st.columns(2)
            col1.metric("Score", st.session_state.score)
            col2.metric("Vies restantes", st.session_state.vies)
            
            st.subheader(f"Calcul : {st.session_state.q} = ?")
            
            with st.form("jeu"):
                rep_eleve = st.number_input("Ta réponse :", step=1)
                bouton_valider = st.form_submit_button("Valider")
                
            if bouton_valider:
                if rep_eleve == st.session_state.r:
                    st.session_state.score += 1
                    st.session_state.msg = "✅ Bonne Réponse !"
                    # On sauvegarde le score à chaque point marqué
                    sauvegarder_score(nom, st.session_state.score) 
                else:
                    st.session_state.vies -= 1
                    st.session_state.msg = f"❌ Faux ! C'était {st.session_state.r}. Tu as perdu une vie."
                
                # Prochaine question si les vies ne sont pas à zéro
                if st.session_state.vies > 0:
                    st.session_state.q, st.session_state.r = generer_question()
                st.rerun()

            if st.session_state.msg: st.info(st.session_state.msg)

        with tab2:
            st.subheader("🏆 Meilleurs Scores de la Classe")
            df_public = lire_scores()
            if not df_public.empty:
                # Affichage du Top 10
                classement = df_public.groupby("Nom")["Score"].max().reset_index()
                classement = classement.sort_values(by="Score", ascending=False).head(10)
                classement.index = range(1, len(classement) + 1)
                st.table(classement)
            else:
                st.info("Aucun match joué pour l'instant.")

else:
    st.info("👋 Écris ton prénom pour commencer.")
