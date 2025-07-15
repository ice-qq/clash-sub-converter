FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝 Python 源码和默认配置目录
COPY . .
COPY config /defaults/config

CMD ["python", "main.py"]
