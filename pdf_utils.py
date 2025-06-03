import fitz
import requests
import sqlite3
import os
import json
import re

# pip install pymupdf

OLLAMA_GEN_URL = "http://localhost:11434/api/generate"

PDF_FOLDER = "pdfs"
DB_PATH = "prompts.db"

REQUESTS_TIMEOUT = 120 # Segundos para la llamada al modelo de OLLAMA
MAX_PAR_LENGHT = 2000 # Caracteres máximos por petición
MIN_PAR_LEN = 50 # La longitud mínima para considerar un párrafo

def pdf_to_text(pdf_path):
    # Extrae todo el texto del pdf y lo guarda en una cadena de texto.
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def pdf_to_paragraphs(text):
    # Divide el texto en párrafos usando dobles saltos en línea; si no hay, divide por oraciones. Filtra textos muy cortos.
    paras = re.split(r'\n\s*\n', text)
    
    if len(paras) <= 1:
        paras = re.findall(r'.+?[\.!?](?:\s+|$)', text)
        
    clean = []
    
    for p in paras:
        p = p.replace('\n', '').strip()
        if len(p) >= MIN_PAR_LEN:
            clean.append(p)
    
    return clean

def split_long_paragraphs(paragraph, max_len = MAX_PAR_LENGHT):
    # Si un párrafo excede el max_len.
    sentences = re.split(r'(?<=[\.!?])\s+', paragraph)
    
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s)+1 <= max_len:
            current = f"{current} {s}".strip()
        else:
            if current:
                chunks.append(current)
            current = s
    
    if current:
        chunks.append(current)
    return chunks

def generar_pregunta(chunk):
    prompt = (f"A partir de este texto, genera UNA PREGUNTA corta y clara cuya respuesta sea exactamente el contenido del texto. Devuelvela solo como texto plano: \n\n {chunk}")
    
    try:
        resp = requests.post(   
            OLLAMA_GEN_URL,
            json = {
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream" : False
            },
            timeout = REQUESTS_TIMEOUT
        )
        
        resp.raise_for_status()
        data = resp.json()
        q = data.get("response", "").strip()
        
        if q:
            return q
        print("Generó texto vacío, se saltará este chunk")
    except Exception as e:
        print(f"Error generado pregunta: {e}")
    return None

def insertar_chunk_en_db(tema, pregunta, respuesta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO prompts_responses(tema, pregunta, respuesta) VALUES (?,?,?)", (tema, pregunta, respuesta)
        )
        
        conn.commit()
        print(f"Insertado: {pregunta}")
        
    except sqlite3.IntegrityError:
        print(f"Duplicado, no insertado: {pregunta}")
    finally:
        conn.close()
        
def procesar_pdf_parrafos(pdf_path):
    # Procesa un PDF; divide en parrafos/frases; para cada uno, si es un muy largo, lo parte en subchunks; genera pregunta y la guarda en la db
    if not os.path.exists(pdf_path):
        print(f"No existe: {pdf_path}")
        return
        
    tema = os.path.basename(pdf_path)
    print(f"Procesando párrafos de: {tema}")
    
    texto = pdf_to_text(pdf_path)
    paras = pdf_to_paragraphs(texto)
    
    print(f"Detectados {len(paras)} párrafos/frases")
    
    for idx, p in enumerate(paras, start = 1):
        subparas = (
            split_long_paragraphs(p)
            
            if len(p) > MAX_PAR_LENGHT
            else [p]
        )
        
        for j, chunk in enumerate(subparas, start = 1):
            print(f"Párrafo {idx}/{len(paras)} - subchunk {j}/{len(subparas)}...", end = "")
            
            pregunta = generar_pregunta(chunk)
            
            if pregunta:
                insertar_chunk_en_db(tema, pregunta, chunk)
                
            else:
                print(f"Saltado")
    print(f"Terminado el PDF: {tema}")
    
def procesar_todos_pdfs():
    os.makedirs(PDF_FOLDER, exist_ok = True)
    pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"No hay pdfs en la carpeta")
        return
    
    for pdf in pdfs:
        procesar_pdf_parrafos(os.path.join(PDF_FOLDER, pdf))
        
    print(f"Todos los pdf han sido procesador por parrafps con subchuking")
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description = "Procesa PDFs por parrafos/subchunks y genera preguntas"
    )
    
    parser.add_argument("--pdf", help = "PDF específico (opcional)", required = False)
    args = parser.parse_args()
    
    if args.pdf:
        procesar_pdf_parrafos(args.pdf)
    else:
        procesar_todos_pdfs