FROM python:3.9-slim

# �A�v���P�[�V�����f�B���N�g�����쐬
WORKDIR /app

# �ˑ��֌W�̃C���X�g�[��
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# �A�v���P�[�V�����R�[�h�̃R�s�[
COPY . .

# Flask�A�v���̋N��
CMD ["python", "app.py"]