#!/bin/bash
echo "Building Docker image for Python Evaluator: cr-sandbox-python..."
docker build -t cr-sandbox-python -f Dockerfile.python .

echo "Building Docker image for JavaScript Evaluator: cr-sandbox-node..."
docker build -t cr-sandbox-node -f Dockerfile.javascript .

echo "Environment sandbox images built successfully."
