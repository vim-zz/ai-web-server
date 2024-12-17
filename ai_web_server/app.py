from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from .chat_handler import ChatHandler

load_dotenv()
app = Flask(__name__)
chat_handler = ChatHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = chat_handler.handle_message(user_message)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
