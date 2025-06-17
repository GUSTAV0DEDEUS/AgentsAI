from flask import Blueprint, render_template, request, redirect, url_for, current_app
from src.flaskr.db import get_db
from datetime import datetime, timedelta
from collections import defaultdict
from google import genai
from google.genai import types
import re


bp = Blueprint(
    'chat',
    __name__,
    template_folder='templates',
    static_folder='../static',
    url_prefix='/chat'
)

@bp.route('/', defaults={'chatId': None})
@bp.route('/<int:chatId>')
def chat(chatId):
    db = get_db()

    if not chatId or not db.execute('SELECT 1 FROM Chat WHERE id = ?', (chatId,)).fetchone():
        cur = db.execute(
            'INSERT INTO Chat (title) VALUES (?)',
            ('Novo Chat',)  
        )
        db.commit()
        new_chat_id = cur.lastrowid
        return redirect(url_for('chat.chat', chatId=new_chat_id))

    messages = db.execute(
        'SELECT role, text, timestamp FROM Message WHERE chat_id = ? ORDER BY timestamp ASC',
        (chatId,)
    ).fetchall()

    rows = db.execute(
        'SELECT id, title, timestamp FROM Chat ORDER BY timestamp DESC'
    ).fetchall()

    grouped_chats = defaultdict(list)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    for row in rows:
        print(f"Processando chat: {row['timestamp']}")
        ts = row['timestamp']
        date_key = ts.date()

        if date_key == today:
            label = 'Today'
        elif date_key == yesterday:
            label = 'Yesterday'
        else:
            label = ts.strftime('%d/%m/%Y')

        grouped_chats[label].append(row)

    return render_template('chat.html', chatId=chatId, messages=messages, grouped_chats=grouped_chats)



def clean_response(html_text):
    html_text = re.sub(r"```html\n?", "", html_text, count=1)
    crase_matches = list(re.finditer(r"```", html_text))
    if crase_matches:
        last_crase = crase_matches[-1]
        html_text = html_text[:last_crase.start()] + html_text[last_crase.end():]
    return html_text.strip()


def call_gemini_api(user_message):
    """Chama a API do Gemini e retorna a resposta."""
    try:
        client = genai.Client(api_key=current_app.config['GEMINI_API_KEY'])
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                # temperature=0.7,
                system_instruction=
                """
                    Você é um assistente de IA útil e amigável.

                    Todas as suas respostas devem ser geradas em HTML, diretamente estruturado com elementos como `<p>`, `<ul>`, `<pre>`, `<code>`, `<h1>`, etc.

                    Nunca inclua as tags `<html>`, `<head>`, `<body>` ou blocos de marcação como ```html ou ``` para indicar que esta retornando HTML.

                    Use tags HTML sem aspas desnecessárias, bem indentadas, e respeite a semântica: use `<pre><code>` para blocos de código, `<ul>` para listas, e assim por diante.

                    Evite comentários HTML e saída extra. Apenas o conteúdo necessário para exibição estruturada.

                    Exemplo de bloco de código correto:
                    <pre><code>@Bean public PasswordEncoder passwordEncoder() {
                        return new BCryptPasswordEncoder();
                    }</code></pre>

                """
            ),
            contents=[user_message]
            
        )
        print(f"Resposta do Gemini: {response.text}")
        html_content = clean_response(response.text)     
        return html_content

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

@bp.route('/newMessage', methods=['POST'])
def create_message():
    """Recebe e salva uma nova mensagem no banco de dados e gera resposta do Gemini."""
    text = request.form.get('message')
    chatId = request.form.get('chatId')
    
    if not text or not chatId:
        return redirect(url_for('chat.chat'))

    db = get_db()

    try:
        db.execute(
            'INSERT INTO Message (chat_id, role, type, text) VALUES (?, ?, ?, ?)',
            (chatId, 'User', 'question', text)
        )
        db.commit()
        print(f"Mensagem do usuário salva: {text}")
        
        gemini_response = call_gemini_api(text)
        
        db.execute(
            'INSERT INTO Message (chat_id, role, type, text) VALUES (?, ?, ?, ?)',
            (chatId, 'Assistant', 'answer', gemini_response)
        )
        db.commit()
        print(f"Resposta do Gemini salva: {gemini_response}")
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        db.rollback()

    return redirect(url_for('chat.chat', chatId=chatId))