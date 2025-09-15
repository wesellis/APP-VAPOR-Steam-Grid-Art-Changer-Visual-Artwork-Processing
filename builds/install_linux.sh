#!/bin/bash
echo "Installing VAPOR for Linux/Steam Deck..."
echo ""

# Create local application directory
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

# Copy executable
cp VAPOR_Linux_v2.0.1 ~/.local/bin/vapor
chmod +x ~/.local/bin/vapor

# Copy desktop file
cp VAPOR.desktop ~/.local/share/applications/
cp Vapor_Logo.png ~/.local/share/icons/vapor.png 2>/dev/null || echo "Logo not found, skipping icon"

# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "Installation complete! VAPOR should now appear in your application menu."
echo "You can also run it from terminal with: vapor"
