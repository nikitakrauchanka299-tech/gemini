import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Получаем API-ключ из настроек сервера
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    req_text = data.get('request', {}).get('original_utterance', '').strip()
    is_new = data.get('session', {}).get('new', False)

    # Приветствие при старте навыка
    if is_new or not req_text:
        return jsonify({
            "response": {
                "text": "Привет! Я Gemini. О чём хочешь спросить?",
                "end_session": False
            },
            "version": "1.0"
        })

    if not model:
        return jsonify({
            "response": {
                "text": "Ошибка: Не настроен API ключ Gemini.",
                "end_session": False
            },
            "version": "1.0"
        })

    try:
        # Просим Gemini отвечать кратко для голоса
        prompt = f"Отвечай кратко, понятно и идеально для голосового воспроизведения. Вопрос: {req_text}"
        response = model.generate_content(prompt)
        reply_text = response.text.strip()
    except Exception as e:
        reply_text = "Произошла ошибка при обращении к Gemini."

    return jsonify({
        "response": {
            "text": reply_text,
            "end_session": False
        },
        "version": "1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
