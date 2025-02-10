from flask import Flask, request, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Criar banco de dados
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            storeName TEXT,
            product TEXT,
            productType TEXT,
            section TEXT,
            spacePass TEXT,
            ladderRequired TEXT,
            receivingRequests TEXT,  -- 🔹 Nova coluna para armazenar "Yes" ou "No"
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
            status TEXT
        )
    """)
    
    # 🔹 Verifica se a coluna já existe; se não, adiciona
    cursor.execute("PRAGMA table_info(observations);")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "receivingRequests" not in columns:
        cursor.execute("ALTER TABLE observations ADD COLUMN receivingRequests TEXT DEFAULT 'N/A'")
        conn.commit()

    conn.close()


# ✅ Verificar se a tabela existe
@app.route("/check_db", methods=["GET"])
def check_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='observations';")
    table_exists = cursor.fetchone()
    conn.close()
    return jsonify({"status": "✅ Banco de dados funcionando!" if table_exists else "❌ ERRO: Tabela 'observations' não existe!"})

# ✅ Salvar uma medição
@app.route("/save", methods=["POST"])
def save_data():
    try:
        data = request.json
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO observations (
                storeName, product, productType, section, spacePass, ladderRequired, receivingRequests,
                size25, notLocatedUnits, observations, startTime, endTime,
                pickingTime, pickingFound, pickingNotFound, reoperatingTime,
                reoperatingManipulated, shopfloorTime, shopfloorManipulated,
                transitsTime, devicesFailuresTime, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("storeName", "N/A"), data.get("product", "N/A"), data.get("productType", "N/A"),
            data.get("section", "N/A"), data.get("spacePass", "N/A"), data.get("ladderRequired", "N/A"),
            data.get("receivingRequests", "N/A"),  # ✅ Agora será salvo no banco de dados
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
    except Exception as e:
        return jsonify({"error": "Erro ao salvar no banco de dados", "details": str(e)}), 500


# ✅ Obter todas as medições
@app.route("/measurements", methods=["GET"])
def get_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM observations")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": row[0], 
            "storeName": row[1], 
            "product": row[2], 
            "productType": row[3], 
            "section": row[4], 
            "spacePass": row[5], 
            "ladderRequired": row[6], 
            "receivingRequests": row[7],  # 🆕 Campo na posição correta
            "size25": row[8], 
            "notLocatedUnits": row[9], 
            "observations": row[10], 
            "startTime": row[11], 
            "endTime": row[12], 
            "pickingTime": row[13], 
            "pickingFound": row[14], 
            "pickingNotFound": row[15], 
            "reoperatingTime": row[16], 
            "reoperatingManipulated": row[17], 
            "shopfloorTime": row[18], 
            "shopfloorManipulated": row[19], 
            "transitsTime": row[20], 
            "devicesFailuresTime": row[21], 
            "status": row[22]
        } for row in rows
    ])


# ✅ Obter o total de unidades medidas
@app.route("/get_units_count", methods=["GET"])
def get_units_count():
    store = request.args.get("store", "").strip()
    product = request.args.get("product", "").strip()
    productType = request.args.get("productType", "").strip()
    section = request.args.get("section", "").strip()

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    if product in ["Shoes", "Perfumery"]:
        cursor.execute("""
            SELECT SUM(pickingFound) FROM observations 
            WHERE storeName = ? AND product = ? 
            AND (section = ? OR section IS NULL OR section = '' OR section = 'N/A')
        """, (store, product, section))
    else:
        cursor.execute("""
            SELECT SUM(pickingFound) FROM observations 
            WHERE storeName = ? AND product = ? 
            AND (productType = ? OR productType IS NULL OR productType = '' OR productType = 'N/A') 
            AND (section = ? OR section IS NULL OR section = '' OR section = 'N/A')
        """, (store, product, productType, section))

    total_units = cursor.fetchone()[0] or 0
    conn.close()
    return jsonify({"store": store, "product": product, "productType": productType, "section": section, "total_units": total_units})

@app.route("/")
def home():
    return jsonify({"message": "API Flask rodando corretamente!"})

import os  # Importando os para pegar variáveis de ambiente

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Render define a porta na variável PORT
    app.run(debug=True, host="0.0.0.0", port=port)




