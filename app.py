import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_ngrok import run_with_ngrok
import requests
import json

# 環境変数の読み込み
load_dotenv()

# アプリケーションの設定
app = Flask(__name__)

# SQLiteの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースモデルの定義
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# LINE Bot からのメッセージ受信
@app.route('/line_webhook', methods=['POST'])
def line_webhook():
    payload = request.get_json()
    line_message = payload['events'][0]['message']['text']
    
    # GROWI検索処理
    growi_result = search_growi(line_message)
    
    # Geminiで要約
    gemini_summary = summarize_with_gemini(growi_result)
    
    return jsonify({'status': 'success', 'summary': gemini_summary})

# GROWI検索機能
def search_growi(query):
    growi_url = os.getenv('GROWI_URL')
    growi_api_key = os.getenv('GROWI_API_KEY')
    
    response = requests.get(f'{growi_url}/_api/pages.get', params={'q': query, 'token': growi_api_key})
    
    if response.status_code == 200:
        return response.json()  # 取得したページ情報を返す
    return "検索結果が見つかりませんでした。"

# Geminiで要約
def summarize_with_gemini(text):
    gemini_url = os.getenv('GEMINI_URL')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    response = requests.post(gemini_url, json={'text': text, 'key': gemini_api_key})
    
    if response.status_code == 200:
        return response.json().get('summary')
    return "要約に失敗しました。"

# 検索履歴を取得
@app.route('/history', methods=['GET'])
def get_history():
    history = SearchHistory.query.all()
    return jsonify([{'query': h.query, 'timestamp': h.timestamp} for h in history])

# 検索処理
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if query:
        # 履歴に保存
        new_history = SearchHistory(query=query)
        db.session.add(new_history)
        db.session.commit()

        # ここで実際の検索処理を追加することができます
        logging.info(f'Search query: {query}')
        return jsonify({'status': 'success', 'query': query})
    return jsonify({'status': 'error', 'message': 'Query is required'})

# メインページ
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()  # データベースの初期化
    run_with_ngrok(app)  # ngrokの自動起動
    app.run(debug=True)
