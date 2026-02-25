# VS Codeのデバッグ実行で `from chatbot.graph` でエラーを出さない対策
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from flask import Flask, render_template, request, make_response, session 
from original.graph import get_bot_response, get_messages_list, memory

# 必要なモジュールをインポート
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint

# 環境変数の取得
load_dotenv("../.env")

# OpenAI APIクライアントを生成
client = OpenAI(api_key=os.environ['API_KEY'])

# モデル名
MODEL_NAME = "gpt-4o-mini"

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用の秘密鍵

@app.route('/', methods=['GET', 'POST'])
def index():
    print("START:index()")
    # セッションからthread_idを取得、なければ新しく生成してセッションに保存
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())  # ユーザー毎にユニークなIDを生成

    # GETリクエスト時は初期メッセージ表示
    if request.method == 'GET':
        # メモリをクリア
        memory.storage.clear()
        # 対話履歴を初期化
        response = make_response(render_template('index.html', messages=[]))
        return response

    # ユーザーからのメッセージを取得
    user_message = request.form['user_message']
    
    # ボットのレスポンスを取得（メモリに保持）
    get_bot_response(user_message, memory, session['thread_id'])

    # メモリからメッセージの取得
    messages = get_messages_list(memory, session['thread_id'])

    # レスポンスを返す
    return make_response(render_template('index.html', messages=messages))

@app.route('/auto-question', methods=['POST'])
def auto_question():
    print("START:auto_question")
    # メモリからメッセージの取得
    messages = get_messages_list(memory, session['thread_id'])

    # 役割や前提の設定
    role = "あなたは質問者です。今までの会話の疑問点を見つけて質問して下さい。"

    # メッセージを格納するリスト
    questioner_messages=[{"role": "system", "content": role}]

    for m in messages:
        if m["class"] == "user-message":
            questioner_messages.append({"role": "user", "content": m["text"]})
        if m["class"] == "bot-message":
            questioner_messages.append({"role": "system", "content": m["text"]})

    # APIへリクエスト
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=questioner_messages,
    )

    # 結果を表示
    for choice in response.choices:
        print("-" * 20)
        print("message:::", choice.message.content.strip())
        response_message = choice.message.content

    print("END:response_message ", response_message)

    # ボットのレスポンスを取得（メモリに保持）
    get_bot_response(response_message, memory, session['thread_id'])

    # メモリからメッセージの取得
    messages = get_messages_list(memory, session['thread_id'])

    # レスポンスを返す
    return make_response(render_template('index.html', messages=messages))

@app.route('/clear', methods=['POST'])
def clear():
    print("START:clear")
    # セッションからthread_idを削除
    session.pop('thread_id', None)

    # メモリをクリア
    memory.storage.clear()
    # 対話履歴を初期化
    response = make_response(render_template('index.html', messages=[]))
    return response

if __name__ == '__main__':
    app.run(debug=True)