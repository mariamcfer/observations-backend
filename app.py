from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 🔥 Agora permite requisições de qualquer origem

# 🔹 Inicializar o banco de dados
def init_db():
    with sqlite3.connect("observations.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                storeName TEXT,
                product TEXT,
                productType TEXT,
                section TEXT,
                spacePass TEXT,
                ladderRequired TEXT,
                receivingRequests TEXT,
                size25 INTEGER,
                notLocatedUnits INTEGER,
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
        ''')
        conn.commit()
    print("✅ Banco de dados configurado corretamente!")

@app.route("/save", methods=["POST"])
def save_measurement():
    data = request.get_json()

    try:
        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO observations (
                    storeName, product, productType, section, spacePass, ladderRequired, receivingRequests,
                    size25, notLocatedUnits, observations, startTime, endTime,
                    pickingTime, pickingFound, pickingNotFound, reoperatingTime, reoperatingManipulated,
                    shopfloorTime, shopfloorManipulated, transitsTime, devicesFailuresTime, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("storeName", "N/A"),
                data.get("product", "N/A"),
                data.get("productType", "N/A"),
                data.get("section", "N/A"),
                data.get("spacePass", "N/A"),
                data.get("ladderRequired", "N/A"),
                data.get("receivingRequests", "N/A"),
                data.get("size25", 0),
                data.get("notLocatedUnits", 0),
                data.get("observations", ""),
                data.get("startTime", "N/A"),
                data.get("endTime", "N/A"),
                data.get("pickingTime", 0),
                data.get("pickingFound", 0),
                data.get("pickingNotFound", 0),
                data.get("reoperatingTime", 0),
                data.get("reoperatingManipulated", 0),
                data.get("shopfloorTime", 0),
                data.get("shopfloorManipulated", 0),
                data.get("transitsTime", 0),
                data.get("devicesFailuresTime", 0),
                "synced"
            ))
            conn.commit()
            new_id = cursor.lastrowid

        return jsonify({"message": "Success", "id": new_id}), 201

    except Exception as e:
        return jsonify({"error": "Erro ao salvar no banco de dados", "details": str(e)}), 500

# 🔹 Garante que todas as respostas tenham CORS ativado
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000, debug=True)
