#!/bin/bash

# Exit on error
set -e

echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

# Check if the build was successful
if [ ! -d "frontend/dist" ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully"

# Check if we have the required secrets
if ! fly secrets list >/dev/null 2>&1; then
    echo "⚠️ No secrets found. Please set up the following secrets:"
    echo "- AUTHOR_SECRET: for authentication"
    echo "- FIREWORKS_API_KEY: for AI model access"
    echo ""
    echo "You can set them using:"
    echo "fly secrets set AUTHOR_SECRET=your_secret FIREWORKS_API_KEY=your_key"
    exit 1
fi

echo "🚀 Deploying to fly.io..."
fly deploy

echo "✨ Deployment complete!" 