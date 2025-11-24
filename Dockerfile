# 构建参数
ARG GIT_VERSION=unknown

# 第一阶段：构建应用
FROM node:18-alpine AS builder

# 设置构建参数
ARG GIT_VERSION

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 可以将版本信息写入环境变量或文件中供应用使用
RUN echo "REACT_APP_GIT_VERSION=${GIT_VERSION}" > .env.production

# 构建应用
RUN npm run build

# 第二阶段：部署应用
FROM nginx:alpine

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制构建好的文件
COPY --from=builder /app/build /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]