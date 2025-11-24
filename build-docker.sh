#!/bin/bash

# 获取项目版本信息
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "unknown")
if [ -z "$VERSION" ] || [ "$VERSION" = "unknown" ]; then
    VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")
fi

# 设置镜像名称和标签
IMAGE_NAME="interview-agent"
IMAGE_TAG="$VERSION"

echo "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"

# 构建 Docker 镜像
docker build \
    --build-arg GIT_VERSION="$VERSION" \
    -t "$IMAGE_NAME:$IMAGE_TAG" \
    -t "$IMAGE_NAME:latest" \
    .

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
    echo "Image tags:"
    echo "  - $IMAGE_NAME:$IMAGE_TAG"
    echo "  - $IMAGE_NAME:latest"
else
    echo "Docker image build failed!"
    exit 1
fi