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
    
@app.route("/observations", methods=["GET"])
def get_observations():
    try:
        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM observations")
            rows = cursor.fetchall()

            # 🔹 Obter os nomes das colunas
            column_names = [description[0] for description in cursor.description]

            # 🔹 Converter os resultados em uma lista de dicionários
            observations = [dict(zip(column_names, row)) for row in rows]

        return jsonify(observations), 200  # 🔹 Certifique-se de que está corretamente indentado

    except Exception as e:
        return jsonify({"error": "Erro ao buscar observações", "details": str(e)}), 500


@app.route("/get_units_count", methods=["GET"])
def get_units_count():
    store = request.args.get("store", "").strip()
    product = request.args.get("product", "").strip()
    product_type = request.args.get("productType", "").strip()
    section = request.args.get("section", "").strip()

    # 🔥 Para "Shoes" e "Perfumery", sempre usar productType = "N/A"
    if product in ["Shoes", "Perfumery"]:
        product_type = "N/A"

    try:
        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            
            # 🔹 Construir a consulta SQL dinamicamente
            query = "SELECT SUM(pickingFound) FROM observations WHERE storeName = ? AND product = ? AND section = ?"
            params = [store, product, section]

            # 🔹 Se NÃO for "Shoes" ou "Perfumery", considerar o productType na query
            if product not in ["Shoes", "Perfumery"]:
                query += " AND productType = ?"
                params.append(product_type)

            cursor.execute(query, params)
            result = cursor.fetchone()[0]
            total_units = result if result is not None else 0  # 🔹 Garante que retorna 0 se não houver resultados

        return jsonify({"units_measured": total_units}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao buscar unidades", "details": str(e)}), 500



# 🔹 Garante que todas as respostas tenham CORS ativado
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

import os

PORT = int(os.environ.get("PORT", 5000))  # Render usa a porta 5000 automaticamente

app.run(host="0.0.0.0", port=PORT, debug=True)