FROM python:3.9-slim

# アプリケーションディレクトリを作成
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Flaskアプリの起動
CMD ["python", "app.py"]