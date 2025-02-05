from flask import Flask, request, Response, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite CORS

# 🔥 Função para GARANTIR que o banco de dados é criado corretamente
def init_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Apagar a tabela antiga e criar uma nova
        print("🚨 Apagando tabela antiga e criando uma nova...")
        cursor.execute("DROP TABLE IF EXISTS observations")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                storeName TEXT,
                product TEXT,
                productType TEXT,
                section TEXT,
                spacePass TEXT,
                ladderRequired TEXT,
                size25 TEXT,
                notLocatedUnits TEXT,
                observations TEXT,
                startTime TEXT,
                endTime TEXT,
                pickingTime INTEGER,
                pickingFound INTEGER,
                pickingNotFound INTEGER,
                reoperatingTime INTEGER,
                reoperatingManipulated INTEGER,
                shopfloorTime INTEGER,
                shopfloorManipulated INTEGER,
                transitsTime INTEGER,
                devicesFailuresTime INTEGER,
                status TEXT,
                flagged_observation TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Banco de dados RECRIADO com sucesso!")
    except Exception as e:
        print("❌ ERRO ao criar banco de dados:", e)


# ✅ **Verificar se a tabela existe**
@app.route("/check_db", methods=["GET"])
def check_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='observations';")
        table = cursor.fetchone()
        conn.close()

        if table:
            return jsonify({"status": "✅ Tabela 'observations' existe!"})
        else:
            return jsonify({"status": "❌ ERRO: Tabela 'observations' NÃO existe!"})
    except Exception as e:
        return jsonify({"status": f"Erro ao verificar DB: {str(e)}"})


# ✅ **Salvar medições**
@app.route("/save", methods=["POST"])
def save_data():
    data = request.json  
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    print("📥 Dados recebidos:", data)

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO observations (
            storeName, product, productType, section, spacePass, ladderRequired, 
            size25, notLocatedUnits, observations, startTime, endTime, 
            pickingTime, pickingFound, pickingNotFound, reoperatingTime, 
            reoperatingManipulated, shopfloorTime, shopfloorManipulated, 
            transitsTime, devicesFailuresTime, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("storeName", "N/A"), data.get("product", "N/A"), data.get("productType", "N/A"),
        data.get("section", "N/A"), data.get("spacePass", "N/A"), data.get("ladderRequired", "N/A"),
        data.get("size25", "N/A"), data.get("notLocatedUnits", "N/A"), data.get("observations", "N/A"),
        data.get("startTime", "N/A"), data.get("endTime", "N/A"), data.get("pickingTime", 0),
        data.get("pickingFound", 0), data.get("pickingNotFound", 0), data.get("reoperatingTime", 0),
        data.get("reoperatingManipulated", 0), data.get("shopfloorTime", 0), data.get("shopfloorManipulated", 0),
        data.get("transitsTime", 0), data.get("devicesFailuresTime", 0), "synced"
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "✅ Data saved successfully!", "id": new_id})


# ✅ **Página inicial**
@app.route("/")
def index():
    return "🚀 Flask is running! Test /measurements for data."


# ✅ **Rodando o servidor**
if __name__ == "__main__":
    init_db()  # 🔥 GARANTE QUE O BANCO É CRIADO NO INÍCIO
    app.run(debug=True, host="0.0.0.0", port=5000)
