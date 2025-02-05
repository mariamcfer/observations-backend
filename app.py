from flask import Flask, request, Response, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ✅ Função para criar/recriar banco de dados
def init_db():
    try:
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
        conn.commit()
        conn.close()
        print("✅ Banco de dados criado/verificado com sucesso!")
    except Exception as e:
        print(f"❌ ERRO ao criar banco de dados: {e}")


# ✅ Testar se a tabela existe
@app.route("/check_db", methods=["GET"])
def check_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='observations';")
        table_exists = cursor.fetchone()
        conn.close()

        if table_exists:
            return jsonify({"status": "✅ Banco de dados está funcionando!"})
        else:
            return jsonify({"status": "❌ ERRO: Tabela 'observations' NÃO existe!"})
    except Exception as e:
        return jsonify({"error": "Erro ao acessar banco de dados", "details": str(e)}), 500


# ✅ Salvar uma medição
@app.route("/save", methods=["POST"])
def save_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Nenhum dado recebido"}), 400

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
    except Exception as e:
        return jsonify({"error": "Erro ao salvar no banco de dados", "details": str(e)}), 500


# ✅ Obter todas as medições
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
        return jsonify({"error": "Erro ao acessar banco de dados", "details": str(e)}), 500


# ✅ Página inicial
@app.route("/")
def index():
    return "🚀 Flask API is running! Try /check_db to verify 'data.db' status."


# ✅ Iniciar servidor e criar DB
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

    # ✅ Endpoint para obter o total de unidades medidas (pickingFound) para uma combinação específica
@app.route("/get_count", methods=["GET"])
def get_count():
    try:
        store = request.args.get("storeName")
        product = request.args.get("product")
        productType = request.args.get("productType", "N/A")
        section = request.args.get("section", "N/A")

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # 🛑 Se for Shoes ou Perfumery, ignoramos a secção
        if product in ["Calzado", "Perfumeria"]:
            cursor.execute("""
                SELECT SUM(pickingFound) FROM observations 
                WHERE storeName = ? AND product = ?
            """, (store, product))
        else:
            cursor.execute("""
                SELECT SUM(pickingFound) FROM observations 
                WHERE storeName = ? AND product = ? AND productType = ? AND section = ?
            """, (store, product, productType, section))

        total_units = cursor.fetchone()[0] or 0  # Se for None, retorna 0
        conn.close()

        return jsonify({"store": store, "product": product, "productType": productType, "section": section, "total_units": total_units})

    except Exception as e:
        return jsonify({"error": "Erro ao obter contagem", "details": str(e)}), 500

