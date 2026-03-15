import os
import logging
from openai import OpenAI
from .models import Producto, Categoria
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_groq_client():
    """Inicializar cliente de Groq con validación"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        logger.error(" Falta GROQ_API_KEY en variables de entorno")
        raise ValueError("Configura la variable de entorno GROQ_API_KEY")
    
    return OpenAI(
        api_key=api_key,
        base_url='https://api.groq.com/openai/v1'
    )

def preguntar_chatbot(pregunta, max_productos=15):
    """Chatbot inteligente para Repostería 'Dalas'"""
    try:
        productos = Producto.query.filter(
            Producto.stock > 0
        ).limit(max_productos).all()
        
        if not productos:
            return "Lo siento, actualmente no tenemos productos disponibles. ¿En qué más puedo ayudarte?"
        
        lista_productos = "\n".join([
            f"{p.nombre} - ${p.precio:.2f} (Stock: {p.stock})"
            f"{' - ' + p.categoria.nombre if p.categoria else ''}"
            for p in productos
        ])
        
        sistema_prompt = f"""Eres un asistente virtual experto en repostería de la tienda "Ventas".

 NUESTROS PRODUCTOS DISPONIBLES:
{lista_productos}

 INSTRUCCIONES:
1. Responde SIEMPRE en español
2. Usa formato: "${{precio:.2f}}" para precios
3. Si un producto no está en la lista, di que no lo tenemos
4. Mantén respuestas concisas (3-4 oraciones)
5. NUNCA inventes productos o precios

Fecha: {datetime.now().strftime('%d/%m/%Y')}"""

        client = get_groq_client()
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sistema_prompt},
                {"role": "user", "content": pregunta}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1.0
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f" Error en chatbot: {str(e)}")
        return f" Error técnico: {str(e)}. Intenta de nuevo."
