import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Cargar el modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2") # Modelo ligero y rapido

def connect_db():
    return sqlite3.connect("prompts.db")

def cargar_preguntas_y_respuestas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT id, pregunta, respuesta FROM prompts_responses
                   ''')
    data = cursor.fetchall()
    conn.close()
    return data

def construir_Embeddings():
    preguntas_y_respuestas = cargar_preguntas_y_respuestas()
    preguntas = [p[1] for p in preguntas_y_respuestas]
    embeddings = model.encode(preguntas, convert_to_tensor = True)    
    return preguntas_y_respuestas, embeddings

def buscar_respuesta_similar(pregunta_usuario):
    preguntas_y_respuestas, embeddings = construir_Embeddings()
    embedding_user = model.encode(pregunta_usuario, convert_to_tensor = True)
    
    # Calcular similitud del coseno
    scores = util.cos_sim(embedding_user, embeddings)[0]
    max_score = scores.max().item()
    
    if max_score >= 0.7:
        best_idx = scores.argmax().item()
        pregunta_similar, respuesta = preguntas_y_respuestas[best_idx][1], preguntas_y_respuestas[best_idx][2]
        return(pregunta_similar, respuesta)
    else:
        return None

def obtene_few_shots_por_tema(tema):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT pregunta, respuesta FROM prompts_responses WHERE tema = ?", (tema,))
    
    ejemplos = cursor.fetchall()
    conn.close()
    
    return "\n".join([f"Usuario: {p}\nExperto: {r}" for p, r in ejemplos])