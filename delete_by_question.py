pregunta_a_borrar = "¿Qué es @Entity?"

conn = sqlite3.connect("prompts.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM prompts_responses WHERE pregunta = ?", (pregunta_a_borrar,))
conn.commit()
conn.close()
print("Registro eliminado.")
