#!/bin/bash

# Registry name
SERVICE=$1
REGISTRY_PROJECT="eskeptdev"
REGISTRY_USER="eskeptdev"

if [ -z "$SERVICE" ]; then
    SERVICE="backend"
    echo "No service specified, defaulting to backend."
fi

if [ "$SERVICE" == "backend" ]; then
    SERVICE_NAME="ecommerce-backend"
elif [ "$SERVICE" == "worker" ]; then
    SERVICE_NAME="ecommerce-worker"
else
    echo "Invalid service: ${SERVICE}"
    exit 1
fi

# Get the current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Try to get git commit hash if available
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "nogit")

# Generate unique tag
TAG="${SERVICE_NAME}:${TIMESTAMP}_${GIT_HASH}"

# Build the image
echo "Building Docker image with tag: ${TAG}"
docker build -t ${TAG} --platform linux/amd64 -f Dockerfile .
echo "Image built successfully!"

# Tag as latest
docker tag ${TAG} ${REGISTRY_PROJECT}/${TAG}

echo "Image tag: ${TAG}"
echo "Registry image tag: ${REGISTRY_PROJECT}/${TAG}"

docker push ${REGISTRY_PROJECT}/${TAG}
