import fitz  # PyMuPDF
import openai
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def ask_question_to_gpt(api_key, text, question):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en responder preguntas sobre documentos PDF."},
            {"role": "user", "content": f"El siguiente texto es un documento PDF:\n\n{text}\n\nPregunta: {question}\nRespuesta:"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or 'api_key' not in request.form:
            flash('Faltan datos en el formulario')
            return redirect(request.url)
        
        api_key = request.form['api_key']
        file = request.files['file']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)
        
        if file and api_key:
            file_path = 'uploaded.pdf'
            file.save(file_path)
            
            # Extraer texto del PDF
            document_text = extract_text_from_pdf(file_path)
            
            # Obtener la pregunta del formulario
            question = request.form['question']
            
            # Obtener la respuesta de GPT-3.5
            answer = ask_question_to_gpt(api_key, document_text, question)
            
            return render_template('index.html', api_key=api_key, question=question, answer=answer)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
