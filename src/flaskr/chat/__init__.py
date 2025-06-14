from flask import Blueprint, render_template

bp = Blueprint(
    'chat',
    __name__,
    template_folder='templates', 
    static_folder='../static', 
    url_prefix='/chat'
)

@bp.route('/')    
def index():
    return render_template('chat.html')