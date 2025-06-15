from flask import Blueprint, render_template, request, redirect, url_for
from src.flaskr.db import get_db
from datetime import datetime, timedelta
from collections import defaultdict

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
            ('Novo Chat',)  # Tupla de 1 elemento precisa da vírgula
        )
        db.commit()
        new_chat_id = cur.lastrowid
        return redirect(url_for('chat.chat', chatId=new_chat_id))

    # Buscar mensagens do chat atual
    messages = db.execute(
        'SELECT role, text, timestamp FROM Message WHERE chat_id = ? ORDER BY timestamp ASC',
        (chatId,)
    ).fetchall()

    # Buscar todos os chats para histórico (agrupados por dia)
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


@bp.route('/newMessage', methods=['POST'])
def create_message():
    """Recebe e salva uma nova mensagem no banco de dados."""
    text = request.form.get('message')
    chatId = request.form.get('chatId')
    role = 'User'
    type = 'question'
    db = get_db()

    # Verificação: se não veio chatId, redireciona para criação de novo chat
    if not chatId:
        return redirect(url_for('chat.chat'))

    try:
        db.execute(
            'INSERT INTO Message (chat_id, role, type, text) VALUES (?, ?, ?, ?)',
            (chatId, role, type, text)
        )
        db.commit()
        print(f"Mensagem salva: {text}")
    except Exception as e:
        print(f"Erro ao salvar mensagem: {e}")

    return redirect(url_for('chat.chat', chatId=chatId))
