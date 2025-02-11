from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Caminho do banco de dados no Render
DB_PATH = os.path.join(os.path.dirname(__file__), "observations.db")

# 🔹 Função para inicializar o banco de dados
def init_db():
    print("🔄 Inicializando o banco de dados...")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store TEXT NOT NULL,
                process INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                value TEXT NOT NULL  -- 🔥 JSON armazenado como string
            )
        ''')
        conn.commit()
    print("✅ Banco de dados inicializado corretamente!")

# 🔥 Chama a inicialização do banco de dados ao iniciar o app
init_db()

@app.route("/")
def home():
    return jsonify({"message": "Observations Backend is running!"}), 200

@app.route("/save", methods=["POST"])
def save_measurement():
    data = request.get_json()

    required_fields = ["store", "process", "start_time", "end_time", "value"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obrigatório '{field}' está ausente!"}), 400

    required_value_fields = ["spacePass", "ladderRequired", "receivingRequests", "detailedSearch"]
    for field in required_value_fields:
        if field not in data["value"] or not data["value"][field]:
            return jsonify({"error": f"Campo obrigatório '{field}' está ausente ou vazio!"}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # 🔹 Verifica se a medição já existe antes de inserir
            cursor.execute('''
                SELECT COUNT(*) FROM measurements 
                WHERE store = ? AND start_time = ? AND value = ?
            ''', (data["store"], data["start_time"], json.dumps(data["value"])))

            if cursor.fetchone()[0] > 0:
                return jsonify({"message": "Medição já registrada, ignorando duplicação"}), 200

            cursor.execute('''
                INSERT INTO measurements (store, process, start_time, end_time, value)
                VALUES (?, ?, ?, ?, ?)
            ''', (data["store"], int(data["process"]), data["start_time"], data["end_time"], json.dumps(data["value"])))

            conn.commit()
            new_id = cursor.lastrowid

        return jsonify({"message": "Success", "id": new_id}), 201

    except Exception as e:
        return jsonify({"error": "Erro ao salvar no banco de dados", "details": str(e)}), 500


@app.route("/observations", methods=["GET"])
def get_observations():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM measurements")
            rows = cursor.fetchall()

            column_names = [description[0] for description in cursor.description]
            observations = [dict(zip(column_names, row)) for row in rows]

            for obs in observations:
                obs["value"] = json.loads(obs["value"])
                obs["value"]["detailedSearch"] = obs["value"].get("detailedSearch", "N/A")  # 🔥 Garante exibição correta

        return jsonify(observations), 200  

    except Exception as e:
        return jsonify({"error": "Erro ao buscar observações", "details": str(e)}), 500

@app.route("/get_units_count", methods=["GET"])
def get_units_count():
    store = request.args.get("store", "")
    product = request.args.get("product", "")
    product_type = request.args.get("productType", "")
    section = request.args.get("section", "")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            if product in ["Shoes", "Perfumery"]:
                query = '''
                    SELECT SUM(CAST(json_extract(value, '$.pickingFound') AS INTEGER))
                    FROM measurements
                    WHERE store = ? AND json_extract(value, '$.product') = ?
                '''
                cursor.execute(query, (store, product))
            else:
                query = '''
                    SELECT SUM(CAST(json_extract(value, '$.pickingFound') AS INTEGER))
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

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/check_db", methods=["GET"])
def check_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='measurements'")
            result = cursor.fetchone()
            if result:
                return jsonify({"message": "✅ A tabela 'measurements' EXISTE no banco de dados!"}), 200
            else:
                return jsonify({"error": "❌ A tabela 'measurements' NÃO EXISTE!"}), 500
    except Exception as e:
        return jsonify({"error": "Erro ao verificar banco de dados", "details": str(e)}), 500



if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)