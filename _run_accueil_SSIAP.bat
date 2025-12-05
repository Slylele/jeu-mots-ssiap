@echo off
color 72
Title Revisions SSIAP
cls

:: Récupère le chemin du dossier courant (où se trouve le .bat)
set dirPath=%~dp0

:: Remplace le chemin réseau si nécessaire
set dirPath=%dirPath:\\Dahergroup.com\dfs-daher$\Secteurs\=T:\%


:: Lance l'application Streamlit
streamlit run SSIAP_Revisions.py