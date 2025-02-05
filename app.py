from flask import Flask, request, Response, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse o backend sem bloqueios de CORS


# 🔹 Função para inicializar o banco de dados (sem apagar dados)
def init_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                storeName TEXT,
                product TEXT,
                typeOfProduct TEXT,
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
        print("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print("❌ Erro ao inicializar o banco de dados:", e)


# 🔥 **Função para FORÇAR a recriação do banco de dados (cuidado!)**
def reset_db():
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        
        # 🚨 Apagar completamente a tabela antiga e criar do zero
        cursor.execute("DROP TABLE IF EXISTS observations")
        
        cursor.execute("""
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                storeName TEXT,
                product TEXT,
                typeOfProduct TEXT,
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
        print("❌ Erro ao recriar o banco de dados:", e)


# ✅ **Salvar medições**
@app.route("/save", methods=["POST"])
def save_data():
    data = request.json  
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    print("Dados recebidos:", data)

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO observations (
            storeName, product, typeOfProduct, section, spacePass, ladderRequired, 
            size25, notLocatedUnits, observations, startTime, endTime, 
            pickingTime, pickingFound, pickingNotFound, reoperatingTime, 
            reoperatingManipulated, shopfloorTime, shopfloorManipulated, 
            transitsTime, devicesFailuresTime, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("storeName", "N/A"), data.get("product", "N/A"), data.get("typeOfProduct", "N/A"),
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

    return jsonify({"message": "Data saved successfully!", "id": new_id})


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
                "id": row[0], "storeName": row[1], "product": row[2], "typeOfProduct": row[3], "section": row[4],
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


# ✅ **Reportar erro em uma medição**
@app.route("/report_error", methods=["POST"])
def report_error():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    measurement_id = data.get("id")

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE observations SET flagged_observation = ? WHERE id = ?", ("Yes", measurement_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Error flagged successfully!"})


# ✅ **Rota inicial para testar se a API está rodando**
@app.route("/")
def index():
    return "Flask is running! Access /measurements for data or use the app interface."


# ✅ **Rodando o servidor e forçando a recriação do banco**
if __name__ == "__main__":
    init_db()  # Criar banco se não existir
    reset_db()  # 🔥 Apagar e recriar banco (ATENÇÃO: Isso deleta todos os dados!)
    app.run(debug=True, host="0.0.0.0", port=5000)
