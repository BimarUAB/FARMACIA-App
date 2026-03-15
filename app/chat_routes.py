from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from .ai_chat import preguntar_chatbot
from datetime import datetime


chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_page():
    """Página del chat"""
    return render_template('chatbot.html')

@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """API del chatbot"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '').strip()
        
        if not pregunta:
            return jsonify({
                'error': 'La pregunta no puede estar vacía',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Obtener respuesta del chatbot
        respuesta = preguntar_chatbot(pregunta)
        
        return jsonify({
            'pregunta': pregunta,
            'respuesta': respuesta,
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
        
    except Exception as e:
        print(f"ERROR EN CHATBOT: {str(e)}")  
        return jsonify({
            'error': f'Error en el servidor: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'success': False
        }), 500
