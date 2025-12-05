import streamlit as st
import pandas as pd
import random
import os
import time
try:
    from streamlit_scroll_to_top import scroll_to_here
except Exception:
    def scroll_to_here(*args, **kwargs):
        pass

# -----------------------------
# Session state initialisation
# -----------------------------
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False
if 'scroll_to_bottom' not in st.session_state:
    st.session_state.scroll_to_bottom = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if st.session_state.scroll_to_top:
    scroll_to_here(0, key='top')
    st.session_state.scroll_to_top = False

if st.session_state.start_time is None:
    st.session_state.start_time = time.time()

# -----------------------------
# Locate workbook
# -----------------------------
script_dir1 = os.path.dirname(__file__)
script_dir2 = os.getcwd()
try:
    _ = os.listdir(script_dir1)
    script_dir = script_dir1
except Exception:
    script_dir = script_dir2

st.set_page_config(layout="wide")

st.title("📘 QCM 2025", anchor="qcm_title")
excel_name = "SSIAP_Questions_2025.xlsx"
excel_path = os.path.join(script_dir, excel_name)

_df_questions_all = pd.read_excel(excel_path, sheet_name="Liste_Questions", engine="openpyxl")
_df_uv_all = pd.read_excel(excel_path, sheet_name="Liste_UV", engine="openpyxl")

_df_questions_all = _df_questions_all.rename(columns={c: c.strip() for c in _df_questions_all.columns})
_df_uv_all = _df_uv_all.rename(columns={c: c.strip() for c in _df_uv_all.columns})

file_choice = st.radio("📂 Sélectionnez les questions à utiliser :", ["QCM par UV", "VRAC examen blanc"], index=0)

if file_choice == "QCM par UV":
    df_questions = _df_questions_all[_df_questions_all['UV'].astype(str).str.startswith('UV')].copy()
    df_uv = _df_uv_all[_df_uv_all['UV'].astype(str).str.startswith('UV')].copy()
else:
    df_questions = _df_questions_all[_df_questions_all['UV'].astype(str).str.startswith('VRAC')].copy()
    df_uv = _df_uv_all[_df_uv_all['UV'].astype(str).str.startswith('VRAC')].copy()

uv_in_questions = df_questions["UV"].unique()
df_uv_filtered = df_uv[df_uv["UV"].isin(uv_in_questions)]
uv_display_list = [f"{row['UV']} - {row.get('Description', row.get('Titre', ''))}" for _, row in df_uv_filtered.iterrows()]

selected_uv_display = st.selectbox("📚 Choisissez une UV :", uv_display_list) if len(uv_display_list) > 0 else None
if selected_uv_display is None:
    st.warning("Aucune UV disponible.")
    st.stop()
selected_uv = selected_uv_display.split(" - ")[0]

uv_questions = df_questions[df_questions["UV"] == selected_uv].copy()
nb_questions = len(uv_questions)

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "last_file" not in st.session_state:
    st.session_state.last_file = file_choice
if "last_uv" not in st.session_state:
    st.session_state.last_uv = selected_uv

if (st.session_state.last_file != file_choice) or (st.session_state.last_uv != selected_uv) \
        or "question_order" not in st.session_state or st.session_state.get("reset_flag", False):
    st.session_state.last_file = file_choice
    st.session_state.last_uv = selected_uv
    st.session_state.submitted = False
    st.session_state.user_answers = {}
    st.session_state.question_order = random.sample(list(uv_questions.index), len(uv_questions))
    st.session_state.reset_flag = False
    st.session_state.start_time = time.time()
    st.session_state.end_time = None

if st.button("🔄 Réinitialiser le questionnaire"):
    st.session_state.submitted = False
    st.session_state.user_answers = {}
    st.session_state.reset_flag = True
    st.session_state.start_time = time.time()
    st.rerun()

uv_questions = uv_questions.loc[st.session_state.question_order]
st.header(f"📝 Questions pour {selected_uv} ({nb_questions} questions)")

correct_col = "BonneRéponse" if "BonneRéponse" in uv_questions.columns else ("Bonne Réponse" if "Bonne Réponse" in uv_questions.columns else None)
if correct_col is None:
    st.error("Colonne des bonnes réponses introuvable.")
    st.stop()

def parse_correct(s: str):
    if pd.isna(s):
        return []
    return sorted([x.strip().upper() for x in str(s).replace(';', ',').split(',') if x.strip()])

ALL_LETTERS = list("ABCDEFG")
score = 0
question_num = 0

for index, row in uv_questions.iterrows():
    question_num += 1
    st.markdown("---")
    question_key = f"Q{row.get('Numéro Question', index)}"
    st.markdown(
        f"<p style='margin-top:0; margin-bottom:0px; margin:0; padding:0; line-height:100%;'>"
        f"<span style='font-weight:bold;'>Question {question_num}</span>"
        f" : {row['Intitulé de la Question']}"
        f"</p>",
        unsafe_allow_html=True)
    st.markdown("<p style='color:red; margin-top:0; margin-bottom:0px;'></p>", unsafe_allow_html=True)

    options = {k: row.get(f"Proposition {k}") for k in ALL_LETTERS if pd.notna(row.get(f"Proposition {k}"))}
    correct_letters = parse_correct(row.get(correct_col, ""))

    if not st.session_state.submitted:
        user_choice = []
        for opt_key, opt_text in options.items():
            checked = st.checkbox(f"{opt_key} - {opt_text}", key=f"{question_key}_{opt_key}")
            if checked:
                user_choice.append(opt_key)
        st.session_state.user_answers[question_key] = user_choice
    else:
        user_choice = st.session_state.user_answers.get(question_key, [])
        selected_set = set(user_choice)
        correct_set = set(correct_letters)
        # ✅ Affichage des réponses
        if len(user_choice) == 0:
            st.markdown("<p style='color:red; margin-top:0; margin-bottom:0px; margin:0; padding:0; padding-left:25px; text-indent:-25px; line-height:125%;'>❌ Aucune sélection</p>", unsafe_allow_html=True)
        for opt_key, opt_text in options.items():
            if opt_key in selected_set and opt_key in correct_set:
                st.markdown(f"<p style='color:green; margin-top:0; margin-bottom:0px; margin:0; padding:0; padding-left:45px; text-indent:-45px; line-height:125%;'>✅ {opt_key} - {opt_text}</p>", unsafe_allow_html=True)
            elif opt_key in selected_set and opt_key not in correct_set:
                st.markdown(f"<p style='color:red; margin-top:0; margin-bottom:0px; margin:0; padding:0; padding-left:45px; text-indent:-45px; line-height:125%;'>❌ {opt_key} - {opt_text}</p>", unsafe_allow_html=True)
            elif opt_key in correct_set and opt_key not in selected_set:
                st.markdown(f"<p style='color:red; margin-top:0; margin-bottom:0px; margin:0; padding:0; padding-left:45px; text-indent:-45px; line-height:125%;'>✅ {opt_key} - {opt_text}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='margin-top:0; margin-bottom:0px; margin:0; padding:0; margin-left:25px; padding-left:20px; text-indent:-20px; line-height:125%;'>{opt_key} - {opt_text}</p>", unsafe_allow_html=True)
        if selected_set == correct_set:
            score += 1
        if len(correct_set) > 0:
            st.caption(f"Réponse(s) attendue(s) : {', '.join(sorted(correct_set))}")

if not st.session_state.submitted:
    if st.button("✅ Soumettre mes réponses"):
        st.session_state.submitted = True
        st.session_state.end_time = time.time()
        st.session_state.scroll_to_bottom = True
        st.rerun()
else:
    total_questions = len(uv_questions)
    score_out_of_20 = round((score / total_questions) * 20, 2) if total_questions else 0.0
    st.markdown("---")
    st.markdown(f"🏆 Score : {score_out_of_20}/20")
    st.markdown(f"Score total : {score}/{total_questions}")
    elapsed = st.session_state.end_time - st.session_state.start_time if st.session_state.end_time else 0
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    st.markdown(f"⏱ Temps total : {minutes:02d}:{seconds:02d}")
    avg_per_question = elapsed / total_questions if total_questions else 0
    avg_minutes = int(avg_per_question // 60)
    avg_seconds = int(avg_per_question % 60)
    st.markdown(f"Temps moyen par question : {avg_minutes:02d}:{avg_seconds:02d}")
    if st.button("🔄 Réinitialiser le questionnaire "):
        st.session_state.submitted = False
        st.session_state.user_answers = {}
        st.session_state.reset_flag = True
        st.session_state.scroll_to_top = True
        st.session_state.start_time = time.time()
        st.rerun()

st.markdown("----")
if st.session_state.scroll_to_bottom:
    scroll_to_here(0, key='bottom')
    st.session_state.scroll_to_bottom = False
st.markdown("<a href='#qcm_title'>Haut de page</a>", unsafe_allow_html=True)
st.title("", anchor="bottom_page")