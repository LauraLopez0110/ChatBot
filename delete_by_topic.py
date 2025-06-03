tema = "JPA"

conn = sqlite3.connect("prompts.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM prompts_responses WHERE tema = ?", (tema,))
conn.commit()
conn.close()
print(f"Registros del tema '{tema}' eliminados.")
