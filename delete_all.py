import sqlite3

conn = sqlite3.connect("prompts.db")
cursor = conn.cursor()

# Borra todos los registros
cursor.execute("DELETE FROM prompts_responses")
conn.commit()

# Opcional: reinicia el contador de ID
cursor.execute("DELETE FROM sqlite_sequence WHERE name='prompts_responses'")
conn.commit()

conn.close()
print("Tabla vaciada con éxito.")