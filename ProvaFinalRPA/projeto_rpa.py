import requests
import sqlite3
import re
import smtplib
from email.mime.text import MIMEText

motivoDaApi = "GOSTO MUITO DE ANIMAIS E ESCOLHI POR ESSE MOTIVO A API PROFESSOR"
Aluno = "MARCUS VINICIUS - RA: 2400185"


def coletar_dados_api():
    url = "https://api.thedogapi.com/v1/breeds"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Erro ao acessar a API:", e)
        return []

def criar_banco_dados():
    conn = sqlite3.connect("projeto_rpa.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS racas_dogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            temperamento TEXT,
            vida TEXT,
            altura TEXT,
            peso TEXT,
            imagem_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def inserir_dados(dados):
    conn = sqlite3.connect("projeto_rpa.db")
    cursor = conn.cursor()
    for d in dados:
        cursor.execute("""
            INSERT INTO racas_dogs (nome, temperamento, vida, altura, peso, imagem_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            d.get("name"),
            d.get("temperament", ""),
            d.get("life_span", ""),
            d.get("height", {}).get("metric", ""),
            d.get("weight", {}).get("metric", ""),
            d.get("image", {}).get("url", "")
        ))
    conn.commit()
    conn.close()

def processar_dados():
    conn = sqlite3.connect("projeto_rpa.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dados_processados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            temperamento TEXT,
            possui_friendly INTEGER
        )
    """)

    cursor.execute("SELECT nome, temperamento FROM racas_dogs")
    racas = cursor.fetchall()

    for nome, temperamento in racas:
        possui_friendly = 1 if re.search(r'friendly', temperamento, re.IGNORECASE) else 0
        cursor.execute("""
            INSERT INTO dados_processados (nome, temperamento, possui_friendly)
            VALUES (?, ?, ?)
        """, (nome, temperamento, possui_friendly))

    conn.commit()
    conn.close()

# ------------------------------------------------------
def enviar_email():
    conn = sqlite3.connect("projeto_rpa.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM racas_dogs")
    total_racas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dados_processados WHERE possui_friendly = 1")
    total_friendly = cursor.fetchone()[0]
    conn.close()

    corpo = f"""
    Relatório Automático – Projeto RPA com The Dog API

    Total de raças coletadas: {total_racas}
    Raças com 'friendly' no temperamento: {total_friendly}
    
    API de Raças escolhida por gosto pessoal
    Projeto realizado em Python utilizando requests, SQLite, regex e envio de e-mail automatizado.

    """

    remetente = "mvms2005@gmail.com"
    senha = "pwts uoon zdcf yoca"  
    destinatario = "marcus.msilva@aluno.faculdadeimpacta.com.br"

    msg = MIMEText(corpo)
    msg['Subject'] = "Relatório - Projeto The Dog API"
    msg['From'] = remetente
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(msg)
        print("✅ E-mail enviado com sucesso.")
    except Exception as e:
        print("❌ Falha ao enviar o e-mail:", e)

# -----------------------------
if __name__ == "__main__":
    print("🔄 Coletando dados da API...")
    dados = coletar_dados_api()

    print("💾 Criando banco de dados e salvando dados...")
    criar_banco_dados()
    inserir_dados(dados)

    print("🔍 Processando dados com regex...")
    processar_dados()

    print("📤 Enviando relatório por e-mail...")
    enviar_email()
