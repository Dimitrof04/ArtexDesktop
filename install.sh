#!/bin/bash
echo "Update System and Flatpak apps"

sudo pacman -Syu --noconfirm
flatpak update -y

echo "Install ArtexDesktop"

sudo pacman -S gcc
mkdir -p ~/.config/ArtexDesktop
mkdir -p ~/.local/share/ArtexDesktop
cp ~/ArtexDesktop/ ~/.config/ArtexDesktop/ArtexDesktop.ini

echo "ArtexDesktop instaled"