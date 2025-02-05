from flask import Flask, request, jsonify
import json
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "backup_data.json"

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

# ✅ Salvar dados no backup JSON
def save_to_file(data):
    """ Salva os dados localmente num ficheiro JSON """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        existing_data.append(data)

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4)
    except Exception as e:
        print("❌ Erro ao salvar no ficheiro:", e)

# ✅ Restaurar dados do JSON para o SQLite sem duplicações
def restore_from_backup():
    """ Restaura os dados do JSON para o banco de dados SQLite """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()

            for entry in data:
                cursor.execute("""
                    SELECT COUNT(*) FROM observations WHERE storeName = ? AND product = ? AND startTime = ?
                """, (entry.get("storeName", "N/A"), entry.get("product", "N/A"), entry.get("startTime", "N/A")))

                exists = cursor.fetchone()[0]
                
                if exists == 0:  # Só adiciona se não existir
                    cursor.execute("""
                        INSERT INTO observations (
                            storeName, product, productType, section, spacePass, ladderRequired,
                            size25, notLocatedUnits, observations, startTime, endTime,
                            pickingTime, pickingFound, pickingNotFound, reoperatingTime,
                            reoperatingManipulated, shopfloorTime, shopfloorManipulated,
                            transitsTime, devicesFailuresTime, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.get("storeName", "N/A"), entry.get("product", "N/A"), entry.get("productType", "N/A"),
                        entry.get("section", "N/A"), entry.get("spacePass", "N/A"), entry.get("ladderRequired", "N/A"),
                        entry.get("size25", "N/A"), entry.get("notLocatedUnits", "N/A"), entry.get("observations", "N/A"),
                        entry.get("startTime", "N/A"), entry.get("endTime", "N/A"), entry.get("pickingTime", 0),
                        entry.get("pickingFound", 0), entry.get("pickingNotFound", 0), entry.get("reoperatingTime", 0),
                        entry.get("reoperatingManipulated", 0), entry.get("shopfloorTime", 0), entry.get("shopfloorManipulated", 0),
                        entry.get("transitsTime", 0), entry.get("devicesFailuresTime", 0), "synced"
                    ))

            conn.commit()
            conn.close()
            print("✅ Dados restaurados do backup sem duplicações!")
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")

# ✅ Obter total de unidades medidas
@app.route("/get_units_count", methods=["GET"])
def get_units_count():
    store = request.args.get("store", "").strip()
    product = request.args.get("product", "").strip()
    productType = request.args.get("productType", "").strip()
    section = request.args.get("section", "").strip()

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    if product in ["Shoes", "Perfumery"]:
        cursor.execute("""
            SELECT SUM(pickingFound) FROM observations 
            WHERE storeName = ? AND product = ? 
            AND (section = ? OR section IS NULL OR section = '' OR section = 'N/A')
        """, (store, product, section))
    else:
        cursor.execute("""
            SELECT SUM(pickingFound) FROM observations 
            WHERE storeName = ? AND product = ? 
            AND (productType = ? OR productType IS NULL OR productType = '' OR productType = 'N/A') 
            AND (section = ? OR section IS NULL OR section = '' OR section = 'N/A')
        """, (store, product, productType, section))

    total_units = cursor.fetchone()[0] or 0
    conn.close()

    return jsonify({
        "store": store, 
        "product": product, 
        "productType": productType, 
        "section": section, 
        "total_units": total_units
    })

# ✅ Página inicial
@app.route("/")
def index():
    return "🚀 Flask API is running! Try /check_db to verify 'data.db' status."

# ✅ Iniciar servidor e restaurar backup
if __name__ == "__main__":
    init_db()
    restore_from_backup()  # 🔥 Restaurar dados do backup JSON ao iniciar
    app.run(debug=True, host="0.0.0.0", port=5000)
