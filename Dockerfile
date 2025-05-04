# 构建前端
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 构建后端
FROM python:3.11.5-slim as backend-build
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# 最终镜像
FROM python:3.11.5-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       libgl1-mesa-glx \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       libxrender1 \
       nginx \
 && rm -rf /var/lib/apt/lists/*

# 复制前端构建产物
COPY --from=frontend-build /app/frontend/build /usr/share/nginx/html

# 复制后端代码和依赖
COPY --from=backend-build /app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=backend-build /app/backend/ .

# 创建必要的目录
RUN mkdir -p uploads separated_videos

# 配置nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动脚本
COPY start.sh /app/
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"] 