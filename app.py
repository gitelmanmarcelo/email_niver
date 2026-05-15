import pandas as pd
import smtplib
from datetime import datetime, timedelta
from flask import Flask
from email.message import EmailMessage
import os

app = Flask(__name__)

def enviar_email(assunto, corpo):
    msg = EmailMessage()
    msg.set_content(corpo)
    msg['Subject'] = assunto
    msg['From'] = "marcelo.gitelman@gmail.com"  # Pode ser qualquer nome
    destinatarios = [e.strip() for e in os.getenv("EMAIL_DESTINO").split(',')]
    msg['To'] = ", ".join(destinatarios)

    # Configuração para Brevo/SendGrid
    smtp_server = os.getenv("SMTP_SERVER")  # ex: smtp-relay.brevo.com
    smtp_port = 2525

    try:
        # Usando o protocolo STARTTLS para portas 587
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_KEY"))
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar: {e}")

@app.route('/health-check')
def health_check():
    return "ok", 200


@app.route('/check-birthdays')
def check_birthdays():
    df = pd.read_csv('eventos.csv')
    hoje = datetime.now().strftime('%d/%m')
    amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m')

    msg_corpo = ""
    for _, row in df.iterrows():
        if row['data'] == hoje:
            msg_corpo += f"Hoje: {row['nome']}\n"
        if row['data'] == amanha:
            msg_corpo += f"Amanhã: {row['nome']}\n"

    if msg_corpo:
        enviar_email("Lembrete de Aniversário 🎂", msg_corpo)
        return "E-mail enviado!", 200
    enviar_email("Nenhum aniversário para hoje ou amanhã. Tudo tranquilo!")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
