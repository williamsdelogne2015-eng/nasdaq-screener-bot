import streamlit as st
import yfinance as yf
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

# Fonction envoi email
def send_email(subject, body):
    import os
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    if not EMAIL_USER or not EMAIL_PASS:
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
    except Exception as e:
        print(f"Erreur envoi email: {e}")

# Dashboard
st.title("📈 Screener NASDAQ - Stratégie Williams")
st.write("Analyse automatique des actions ≤ $10 selon tes critères")

tickers = ["AAPL", "TSLA", "AMD", "NVDA"]
data = {}
for t in tickers:
    df = yf.download(t, period="10d", interval="1d")
    if not df.empty:
        last_close = df["Close"].iloc[-1]
        max_10d = df["High"].max()
        drop = (max_10d - last_close) / max_10d * 100
        data[t] = {
            "Dernier cours": round(last_close, 2),
            "Chute 10j %": round(drop, 2)
        }

df_display = pd.DataFrame(data).T
st.dataframe(df_display)

# Alerte si chute > 30%
alerts = df_display[df_display["Chute 10j %"] >= 30]
if not alerts.empty:
    send_email("Alerte Screener NASDAQ", alerts.to_string())
    st.warning("⚠️ Opportunité détectée ! Email envoyé")
