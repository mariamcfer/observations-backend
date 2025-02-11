from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Inicializar o banco de dados corretamente
def init_db():
    with sqlite3.connect("observations.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store TEXT NOT NULL,
                process INTEGER NOT NULL,  -- 🔥 Agora é INTEGER e não TEXT
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                value TEXT NOT NULL  -- 🔥 JSON armazenado como string
            )
        ''')
        conn.commit()
    print("✅ Banco de dados configurado corretamente!")

@app.route("/save", methods=["POST"])
def save_measurement():
    data = request.get_json()

    # 🔥 Verificar se os campos essenciais estão presentes
    required_fields = ["store", "process", "start_time", "end_time", "value"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obrigatório '{field}' está ausente!"}), 400

    try:
        # 🔥 Garantir que os valores de tempo estejam em formato string
        start_time = str(data["start_time"]) if data["start_time"] else "N/A"
        end_time = str(data["end_time"]) if data["end_time"] else "N/A"

        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO measurements (store, process, start_time, end_time, value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data["store"],
                int(data["process"]),  # 🔥 Garantir que process é INTEGER
                start_time,
                end_time,
                json.dumps(data["value"])  # 🔥 Salvar JSON como string
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
            cursor.execute("SELECT * FROM measurements")
            rows = cursor.fetchall()

            # 🔹 Obter os nomes das colunas
            column_names = [description[0] for description in cursor.description]

            # 🔹 Converter os resultados em uma lista de dicionários
            observations = [dict(zip(column_names, row)) for row in rows]

            # 🔥 Converter a string JSON de "value" de volta para um dicionário Python
            for obs in observations:
                obs["value"] = json.loads(obs["value"])

        return jsonify(observations), 200  

    except Exception as e:
        return jsonify({"error": "Erro ao buscar observações", "details": str(e)}), 500


# 🔥 ROTA PARA PEGAR A CONTAGEM DE UNIDADES MEDIDAS
@app.route("/get_units_count", methods=["GET"])
def get_units_count():
    store = request.args.get("store", "")
    product = request.args.get("product", "")
    product_type = request.args.get("productType", "")
    section = request.args.get("section", "")

    try:
        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            
            # 🔥 Se for "Shoes" ou "Perfumery", ignoramos a seção (somamos tudo)
            if product in ["Shoes", "Perfumery"]:
                query = '''
                    SELECT SUM(CAST(json_extract(value, '$.picking_found') AS INTEGER))
                    FROM measurements
                    WHERE store = ? AND json_extract(value, '$.product') = ?
                '''
                cursor.execute(query, (store, product))
            else:
                query = '''
                    SELECT SUM(CAST(json_extract(value, '$.picking_found') AS INTEGER))
                    FROM measurements
                    WHERE store = ? AND json_extract(value, '$.product') = ? 
                    AND json_extract(value, '$.productType') = ? 
                    AND json_extract(value, '$.section') = ?
                '''
                cursor.execute(query, (store, product, product_type, section))

            total_units = cursor.fetchone()[0] or 0

        return jsonify({"units_measured": total_units}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao buscar contagem de unidades", "details": str(e)}), 500


# 🔹 Garante que todas as respostas tenham CORS ativado
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# 🔥 INICIALIZA O BANCO DE DADOS E RODA O APP
if __name__ == "__main__":
    init_db()
    PORT = int(os.environ.get("PORT", 5000))  # Render usa a porta 5000 automaticamente
    app.run(host="0.0.0.0", port=PORT, debug=True)
