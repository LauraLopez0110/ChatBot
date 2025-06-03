from flask import Flask, request, Response, render_template, session, redirect, url_for
from flask_session import Session
from langdetect import detect

import matplotlib.pyplot as plt
import io
from flask import send_file

import requests
import json
import os

from db import buscar_respuesta_similar

from pdf_utils import procesar_todos_pdfs

app = Flask(__name__)
app.secret_key="1234abcd"
app.config['SESSION_TYPE']='filesystem'
Session(app)

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL_NAME = "mistral:instruct"


PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok = True)

@app.route("/")
def home():
    
    pdfs = os.listdir(PDF_FOLDER)
    return render_template("index.html", pdfs = pdfs)



@app.route("/upload_pdf", methods=["GET", "POST"])
def upload_pdf():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return "No se seleccionó ningún archivo.", 400

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return "Nombre de archivo inválido.", 400

        # Guardar el PDF en la carpeta definida
        pdf_path = os.path.join(PDF_FOLDER, pdf_file.filename)
        pdf_file.save(pdf_path)

        return redirect(url_for('home'))

    return render_template("upload_pdf.html")

@app.route("/procesar_pdfs", methods = ["POST"])
def procesar_pdfs():
    procesar_todos_pdfs()
    
    return redirect(url_for('home'))

from db import buscar_respuesta_similar, obtene_few_shots_por_tema

@app.route("/ask", methods=["POST"])
def ask_model():
    user_question = request.json.get("question", "")
    tema = request.json.get("tema", "general")
    
    # Detectar idioma
    try:
        idioma = detect(user_question)
    except:
        idioma = "es"
    
    historial = session.get('historial', [])

    # Detectar idioma actual del historial (miramos el prompt sistema)
    idioma_historial = None
    if historial:
        for msg in historial:
            if msg['role'] == 'system':
                if "You are an expert" in msg['content']:
                    idioma_historial = "en"
                else:
                    idioma_historial = "es"
                break

    # Si el idioma cambió, limpiar historial para iniciar nuevo prompt
    if idioma_historial != idioma:
        historial = []

    # Si no hay historial, iniciar con prompt del idioma correcto
    if not historial:
        if idioma == "en":
            system_prompt = """
            You are an expert assistant on migration information within Colombia. Reply ONLY in English. Be clear, empathetic, and precise.
            """
        else:
            system_prompt = """
            Eres un asistente experto en la información sobre Migración dentro de Colombia. Responde SOLO en español. Sé claro, empático y preciso.
            """
        historial.append({"role": "system", "content": system_prompt})

    # Agregar la pregunta al historial
    historial.append({"role": "user", "content": user_question})

    payload = {
        "model": MODEL_NAME,
        "messages": historial
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        lines = response.text.strip().split('\n')
        respuesta = ""

        for line in lines:
            try:
                data = json.loads(line)
                respuesta += data['message']['content']
            except Exception as e:
                print("Linea mal formada: ", line, "-Error: ", e)

        # Guardar respuesta y actualizar sesión
        historial.append({"role": "assistant", "content": respuesta})
        session['historial'] = historial

        return Response(respuesta, content_type='text/plain')

    except Exception as e:
        print("ERROR EN STREAM", str(e))
        return Response("ERROR EN STREAM: " + str(e), status=500)

         
@app.route("/reset", methods=["POST"])
def reset_chat():
    session.pop('historial', None)
    session.pop('idioma', None) 
    return{"status": "ok", "message": "Historial borrado"}
           
if __name__ == "__main__":
    app.run(port=5000, debug=True)