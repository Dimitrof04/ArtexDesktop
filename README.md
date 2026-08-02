# 🌌 Artex Desktop

A sleek, minimalist, and highly optimized Hyprland configuration.

> [!TIP]
> This build is highly recommended for Arch-based distributions (Arch Linux, CachyOS, Archcraft, EndeavourOS, etc.).

---

## 🛠️ Components & Features

This Hyprland environment is built using the following core software:

* **Window Manager:** [Hyprland](https://hyprland.org/) *(Dynamic tiling Wayland compositor)*
* **Status Bar:** [Waybar](https://github.com/Alexays/Waybar) *(Highly customizable Wayland bar)*
* **App Launcher:** [HyprLaucher](https://wiki.hypr.land/Hypr-Ecosystem/hyprlauncher/)
* **Terminal Emulator:** [Kitty](https://sw.kovidgoyal.net/kitty/) *(Fast, feature-rich, GPU-based terminal)*
* **Wallpaper Manager:** `awww`
* **Screen Locker:** [Hyprlock](https://wiki.hyprland.org/Hypr-ecosystem/hyprlock/) *(Fast, secure screen locker)*

---

## 🚀 Installation

Run the interactive installer script to set up everything automatically:

```bash
sudo pacman -Syu --needed git
git clone https://github.com/Dimitrof04/ArtexDesktop.git
cd ArtexDesktop
chmod +x install.sh
./install.sh
