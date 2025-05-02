# 使用 Python 3.11.5-slim 作为基础镜像
FROM python:3.11.5-slim

# 设置工作目录
WORKDIR /app

# 安装 OpenCV 运行时所需的系统库
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       libgl1-mesa-glx \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       libxrender1 \
 && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传和分离视频目录
RUN mkdir -p uploads separated_videos

# 暴露 Flask 默认端口
EXPOSE 5000

# 环境变量配置
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动应用
CMD ["python", "app.py"]
