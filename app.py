from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse o backend sem bloqueios de CORS


# 🔥 Força a criação do banco de dados e TABELA
def force_reset_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        print("🚨 Apagando tabela antiga e criando uma nova...")
        cursor.execute("DROP TABLE IF EXISTS observations")

        cursor.execute("""
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                storeName TEXT,
                product TEXT,
                productType TEXT,  -- Corrigido para productType ✅
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

        # 🚀 Testa se a tabela realmente existe depois de criar!
        test_db_creation()

    except Exception as e:
        print("❌ ERRO ao recriar banco de dados:", e)


# 🚀 **Testa se a tabela 'observations' realmente existe**
def test_db_creation():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='observations'")
        table_exists = cursor.fetchone()
        conn.close()

        if table_exists:
            print("✅ Verificação: Tabela 'observations' FOI criada corretamente! 🎉")
        else:
            print("❌ ERRO: A tabela 'observations' NÃO foi criada! 😡")
    except Exception as e:
        print("❌ ERRO ao verificar a tabela:", e)


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


# ✅ **Recuperar todas as medições**
@app.route("/measurements", methods=["GET"])
def get_data():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observations")
        rows = cursor.fetchall()
        conn.close()

        measurements = [
            {
                "id": row[0], "storeName": row[1], "product": row[2], "productType": row[3], "section": row[4],
                "spacePass": row[5], "ladderRequired": row[6], "size25": row[7], "notLocatedUnits": row[8],
                "observations": row[9], "startTime": row[10], "endTime": row[11], "pickingTime": row[12],
                "pickingFound": row[13], "pickingNotFound": row[14], "reoperatingTime": row[15],
                "reoperatingManipulated": row[16], "shopfloorTime": row[17], "shopfloorManipulated": row[18],
                "transitsTime": row[19], "devicesFailuresTime": row[20], "status": row[21]
            } for row in rows
        ]
        return jsonify(measurements)
    
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


# ✅ **Verificar se a tabela foi criada**
@app.route("/check-db", methods=["GET"])
def check_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='observations'")
        table_exists = cursor.fetchone()
        conn.close()

        if table_exists:
            return jsonify({"status": "✅ Tabela 'observations' existe no banco de dados!"})
        else:
            return jsonify({"status": "❌ ERRO: Tabela 'observations' NÃO existe!"}), 500

    except Exception as e:
        return jsonify({"error": "Erro ao verificar banco de dados", "details": str(e)}), 500


# ✅ **Testar se a API está rodando**
@app.route("/")
def index():
    return "🚀 Flask is running! Test /measurements for data."


# ✅ **Rodando o servidor**
if __name__ == "__main__":
    force_reset_db()  # 🔥 GARANTE QUE O BANCO É CRIADO NO RENDER
    app.run(debug=True, host="0.0.0.0", port=5000)
