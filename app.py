from flask import Flask, request, Response, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que o front end acesse o back end sem bloqueios de CORS

# Função para inicializar (ou recriar) o banco de dados
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            storeName TEXT,
            type TEXT,
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

# Endpoint para salvar medições
@app.route("/save", methods=["POST"])
def save_data():
    data = request.json  
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    print("Dados recebidos:", data)

    storeName = data.get("storeName", "N/A")
    type_val = data.get("type", "N/A")
    section = data.get("section", "N/A")
    spacePass = data.get("spacePass", "N/A")
    ladderRequired = data.get("ladderRequired", "N/A")
    size25 = data.get("size25", "N/A")                
    notLocatedUnits = data.get("notLocatedUnits", "N/A")  
    observations = data.get("observations", "N/A")
    startTime = data.get("startTime", "N/A")
    endTime = data.get("endTime", "N/A")
    pickingTime = data.get("pickingTime", 0)
    pickingFound = data.get("pickingFound", 0)
    pickingNotFound = data.get("pickingNotFound", 0)
    reoperatingTime = data.get("reoperatingTime", 0)              
    reoperatingManipulated = data.get("reoperatingManipulated", 0)  
    shopfloorTime = data.get("shopfloorTime", 0)
    shopfloorManipulated = data.get("shopfloorManipulated", 0)
    transitsTime = data.get("transitsTime", 0)              
    devicesFailuresTime = data.get("devicesFailuresTime", 0)   

    status = "synced"

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO observations (
            storeName, type, section, spacePass, ladderRequired, size25, notLocatedUnits, observations, startTime, endTime, 
            pickingTime, pickingFound, pickingNotFound, 
            reoperatingTime, reoperatingManipulated, 
            shopfloorTime, shopfloorManipulated, 
            transitsTime, devicesFailuresTime, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        storeName, type_val, section, spacePass, ladderRequired, size25, notLocatedUnits,
        observations, startTime, endTime, pickingTime, pickingFound, pickingNotFound,
        reoperatingTime, reoperatingManipulated, shopfloorTime, shopfloorManipulated,
        transitsTime, devicesFailuresTime, status
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Data saved successfully!", "id": new_id})

# Endpoint para recuperar medições
@app.route("/measurements", methods=["GET"])
def get_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM observations")
    rows = cursor.fetchall()
    conn.close()

    measurements = [
        {
            "id": row[0], "storeName": row[1], "type": row[2], "section": row[3],
            "spacePass": row[4], "ladderRequired": row[5], "size25": row[6],
            "notLocatedUnits": row[7], "observations": row[8], "startTime": row[9],
            "endTime": row[10], "pickingTime": row[11], "pickingFound": row[12],
            "pickingNotFound": row[13], "reoperatingTime": row[14],
            "reoperatingManipulated": row[15], "shopfloorTime": row[16],
            "shopfloorManipulated": row[17], "transitsTime": row[18],
            "devicesFailuresTime": row[19], "status": row[20]
        } for row in rows
    ]
    return Response(json.dumps(measurements, ensure_ascii=False), mimetype="application/json")

# Endpoint para reportar erros
@app.route("/report_error", methods=["POST"])
def report_error():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    measurement_id = data.get("id")
    error_details = data.get("error", "Erro reportado sem detalhes")

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE observations SET status = ? WHERE id = ?", ("errorReported", measurement_id))
    conn.commit()
    conn.close()

    print(f"Erro reportado para a medição {measurement_id}: {error_details}")

    return jsonify({"message": "Error reported successfully!"})

# ✅ **Corrigindo a indentação da rota `/`**
@app.route("/")
def index():
    return "Flask is running! Access /measurements for data or use the app interface."

# ✅ **Inicia o Flask corretamente**
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
