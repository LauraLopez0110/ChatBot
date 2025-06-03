import sqlite3

conn = sqlite3.connect("prompts.db")
cursor = conn.cursor()

cursor.execute(
    """
    
    CREATE TABLE IF NOT EXISTS prompts_responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT NOT NULL,
        pregunta TEXT NOT NULL UNIQUE,
        respuesta TEXT NOT NULL
    )
    
    """
)

conn.commit()
conn.close()
print("Base de datos creada")