from flask import Flask, request, Response, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que o front end acesse o back end sem bloqueios de CORS

# Função para inicializar (ou recriar) o banco de dados
def init_db():
    try:
        print("🔄 Tentando criar/reiniciar o banco de dados...")
        conn = sqlite3.connect("new_data.db")  # 🔥 ALTERADO para garantir um novo banco!
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS observations (
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
        )""")
        conn.commit()
        conn.close()
        print("✅ Banco de dados criado com sucesso!")
    except Exception as e:
        print("❌ Erro ao criar banco de dados:", e)



# Endpoint para salvar medições
@app.route("/save", methods=["POST"])
def save_data():
    data = request.json  
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    print("Dados recebidos:", data)

    storeName = data.get("storeName", "N/A")
    product = data.get("product", "N/A")  # Novo campo
    productType = data.get("productType", "N/A")  # Novo campo
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

    conn = sqlite3.connect("new_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO observations (
            storeName, product, productType, section, spacePass, ladderRequired, size25, notLocatedUnits, 
            observations, startTime, endTime, pickingTime, pickingFound, pickingNotFound, 
            reoperatingTime, reoperatingManipulated, shopfloorTime, shopfloorManipulated, 
            transitsTime, devicesFailuresTime, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        storeName, product, productType, section, spacePass, ladderRequired, size25, notLocatedUnits,
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
    try:
        conn = sqlite3.connect("new_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observations")
        rows = cursor.fetchall()
        conn.close()

        measurements = [
            {
                "id": row[0], "storeName": row[1], "product": row[2],
                "productType": row[3], "section": row[4], "spacePass": row[5], 
                "ladderRequired": row[6], "size25": row[7], "notLocatedUnits": row[8], 
                "observations": row[9], "startTime": row[10], "endTime": row[11], 
                "pickingTime": row[12], "pickingFound": row[13], "pickingNotFound": row[14], 
                "reoperatingTime": row[15], "reoperatingManipulated": row[16], 
                "shopfloorTime": row[17], "shopfloorManipulated": row[18], 
                "transitsTime": row[19], "devicesFailuresTime": row[20], 
                "status": row[21], "flagged_observation": row[22]  
            } for row in rows
        ]
        return Response(json.dumps(measurements, ensure_ascii=False), mimetype="application/json")
    
    except sqlite3.OperationalError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# Endpoint para reportar erros
@app.route("/report_error", methods=["POST"])
def report_error():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    measurement_id = data.get("id")
    error_details = data.get("error", "Erro reportado sem detalhes")

    # Aqui, vamos atualizar o registo para definir que está flagado.
    conn = sqlite3.connect("new_data.db")
    cursor = conn.cursor()
    # Atualize a coluna "flagged_observation" para "Yes"
    cursor.execute("UPDATE observations SET flagged_observation = ? WHERE id = ?", ("Yes", measurement_id))
    conn.commit()
    conn.close()

    print(f"Erro reportado para a medição {measurement_id}: {error_details}")
    return jsonify({"message": "Error flagged successfully!"})


# ✅ **Corrigindo a indentação da rota `/`**
@app.route("/")
def index():
    return "Flask is running! Access /measurements for data or use the app interface."

if __name__ == "__main__":
    print("🔄 Inicializando o banco de dados...")
    init_db()
    print("✅ Banco de dados pronto!")
    app.run(debug=True, host="0.0.0.0", port=5000)



