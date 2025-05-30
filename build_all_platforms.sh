#!/bin/bash
echo "🎨 VAPOR Multi-Platform Build System"
echo "Creating executables for Windows, macOS, Linux, and Steam Deck"
echo ""

echo "🔧 Installing/updating build dependencies..."
pip3 install --upgrade pyinstaller pillow requests

echo ""
echo "🚀 Starting multi-platform build process..."
python3 build_multiplatform.py all

echo ""
echo "✅ Build process complete! Check the 'builds' folder for all executables."
