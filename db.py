import sqlite3

DB_NAME = "user_operations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
                   DROP TABLE IF EXISTS user_operations
                   """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userOpHash TEXT,
            sender TEXT,
            paymaster TEXT,
            nonce TEXT,
            success BOOLEAN,
            actualGasCost LONG INTEGER,
            actualGasUsed LONG INTEGER,
            blockNumber LONG INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_event(event):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_operations (userOpHash, sender, paymaster, nonce, success, actualGasCost, actualGasUsed, blockNumber)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event["userOpHash"],
        event["sender"],
        event["paymaster"],
        event["nonce"],
        event["success"],
        event["actualGasCost"],
        event["actualGasUsed"],
        event["blockNumber"]
    ))
    conn.commit()
    conn.close()

def get_all_events():
    """
    Lit et renvoie tous les enregistrements de la table user_operations.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_operations")
    results = cursor.fetchall()
    conn.close()
    return results