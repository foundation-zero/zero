#!/bin/bash

echo "🏗️  Building Zero UI Component Documentation with VitePress..."
echo ""

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed. Please install it first:"
    echo "npm install -g pnpm"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    pnpm install
fi

# Build the documentation
echo "📚 Building component documentation..."
pnpm docs:build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Documentation built successfully!"
    echo "📁 Output directory: docs/.vitepress/dist"
    echo ""
    echo "To preview the documentation locally:"
    echo "pnpm docs:preview"
    echo ""
    echo "To serve with a simple HTTP server:"
    echo "cd docs/.vitepress/dist && python -m http.server 8080"
else
    echo ""
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi