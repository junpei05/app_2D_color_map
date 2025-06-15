# 1. ベースイメージ
FROM python:3.11-slim

# 2. 必要なライブラリ
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 3. 作業ディレクトリ
WORKDIR /app

# 4. コードとデータをコンテナにコピー
COPY . .

# 5. ポート
EXPOSE 8501

# 6. 起動コマンド
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
