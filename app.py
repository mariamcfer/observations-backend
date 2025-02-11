from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# 🔹 Inicializar o banco de dados
def init_db():
    with sqlite3.connect("observations.db") as conn:
        cursor = conn.cursor()

        # Criar a tabela se não existir
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
                status TEXT DEFAULT 'awaiting'  -- 🔥 Garante que novas medições começam como 'awaiting'
            )
        ''')

        conn.commit()
    
    print("✅ Banco de dados configurado corretamente!")

# 🔹 Rota para salvar uma nova medição
@app.route("/save", methods=["POST"])
def save_measurement():
    data = request.get_json()

    # 🔹 Bloquear medições que ainda não foram sincronizadas no frontend
    if data.get("status") != "synced":
        return jsonify({"error": "Apenas medições sincronizadas podem ser enviadas para o backend."}), 400

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


# 🔹 Rota para verificar o estado do banco de dados
@app.route("/check_db", methods=["GET"])
def check_db():
    try:
        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM observations")
            count = cursor.fetchone()[0]

        return jsonify({"status": "✅ Banco de dados funcionando!", "registros": count})

    except Exception as e:
        return jsonify({"error": "Banco de dados inacessível", "details": str(e)}), 500

# 🔹 Rota para listar TODAS as medições (para recuperação de dados perdidos)
@app.route("/observations", methods=["GET"])
def get_observations():
    try:
        with sqlite3.connect("observations.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM observations ORDER BY id DESC")
            rows = cursor.fetchall()

        observations = [dict(row) for row in rows]
        return jsonify(observations), 200

    except Exception as e:
        return jsonify({"error": "Erro ao buscar medições", "details": str(e)}), 500

# 🔹 Rota para sincronizar medições pendentes
@app.route("/sync", methods=["POST"])
def sync_measurements():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Formato inválido. Esperado um array de medições."}), 400

        with sqlite3.connect("observations.db") as conn:
            cursor = conn.cursor()

            for measurement in data:
                cursor.execute('''
                    INSERT INTO observations (
                        storeName, product, productType, section, spacePass, ladderRequired, receivingRequests,
                        size25, notLocatedUnits, observations, startTime, endTime,
                        pickingTime, pickingFound, pickingNotFound, reoperatingTime, reoperatingManipulated,
                        shopfloorTime, shopfloorManipulated, transitsTime, devicesFailuresTime, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    measurement.get("storeName", "N/A"),
                    measurement.get("product", "N/A"),
                    measurement.get("productType", "N/A"),
                    measurement.get("section", "N/A"),
                    measurement.get("spacePass", "N/A"),
                    measurement.get("ladderRequired", "N/A"),
                    measurement.get("receivingRequests", "N/A"),
                    measurement.get("size25", 0),
                    measurement.get("notLocatedUnits", 0),
                    measurement.get("observations", ""),
                    measurement.get("startTime", "N/A"),
                    measurement.get("endTime", "N/A"),
                    measurement.get("pickingTime", 0),
                    measurement.get("pickingFound", 0),
                    measurement.get("pickingNotFound", 0),
                    measurement.get("reoperatingTime", 0),
                    measurement.get("reoperatingManipulated", 0),
                    measurement.get("shopfloorTime", 0),
                    measurement.get("shopfloorManipulated", 0),
                    measurement.get("transitsTime", 0),
                    measurement.get("devicesFailuresTime", 0),
                    "synced"
                ))

            conn.commit()

        return jsonify({"message": f"{len(data)} medições sincronizadas com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao sincronizar medições", "details": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
