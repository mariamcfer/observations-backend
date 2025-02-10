from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Inicializar o banco de dados
def init_db():
    conn = sqlite3.connect("observations.db")
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
            receivingRequests TEXT,  -- 🔥 Adicionado esse campo
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
    conn.close()

@app.route("/save", methods=["POST"])
def save_measurement():
    data = request.get_json()
    try:
        conn = sqlite3.connect("observations.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO observations (
                storeName, product, productType, section, spacePass, ladderRequired, receivingRequests,
                size25, notLocatedUnits, observations, startTime, endTime,
                pickingTime, pickingFound, pickingNotFound, reoperatingTime, reoperatingManipulated,
                shopfloorTime, shopfloorManipulated, transitsTime, devicesFailuresTime, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["storeName"], data["product"], data["productType"], data["section"],
            data["spacePass"], data["ladderRequired"], data.get("receivingRequests", "N/A"),  # 🔥 Evita erro se não for enviado
            data["size25"], data["notLocatedUnits"], data["observations"], data["startTime"],
            data["endTime"], data["pickingTime"], data["pickingFound"], data["pickingNotFound"],
            data["reoperatingTime"], data["reoperatingManipulated"], data["shopfloorTime"],
            data["shopfloorManipulated"], data["transitsTime"], data["devicesFailuresTime"], data["status"]
        ))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"message": "Success", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao salvar no banco de dados", "details": str(e)}), 500

@app.route("/check_db", methods=["GET"])
def check_db():
    try:
        conn = sqlite3.connect("observations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM observations")
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({"status": "✅ Banco de dados funcionando!", "registros": count})
    except Exception as e:
        return jsonify({"error": "Banco de dados inacessível", "details": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

    import sqlite3

# Conectar ao banco no servidor do Render
conn = sqlite3.connect("observations.db", check_same_thread=False)
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storeName TEXT NOT NULL,
    product TEXT NOT NULL,
    productType TEXT NOT NULL,
    section TEXT NOT NULL,
    spacePass TEXT NOT NULL,
    ladderRequired TEXT NOT NULL,
    receivingRequests TEXT NOT NULL,
    size25 INTEGER NOT NULL,
    notLocatedUnits INTEGER NOT NULL,
    observations TEXT,
    startTime TEXT NOT NULL,
    endTime TEXT NOT NULL,
    pickingTime INTEGER NOT NULL,
    pickingFound INTEGER NOT NULL,
    pickingNotFound INTEGER NOT NULL,
    reoperatingTime INTEGER NOT NULL,
    reoperatingManipulated INTEGER NOT NULL,
    shopfloorTime INTEGER NOT NULL,
    shopfloorManipulated INTEGER NOT NULL,
    transitsTime INTEGER NOT NULL,
    devicesFailuresTime INTEGER NOT NULL,
    status TEXT NOT NULL
);
""")

conn.commit()
conn.close()

print("✅ Banco de dados configurado corretamente!")
