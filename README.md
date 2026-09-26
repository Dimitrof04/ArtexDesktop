# 🎨 ArtexDesktop

> Uma ecossistema moderno e nativo para personalização das principais interfaces de usuário no Linux.

O **ArtexDesktop** é um projeto focado em entregar uma experiência visual fluida, modular e integrada para o ambiente Linux. Ele busca centralizar scripts, temas e utilitários para ajustar a interface ao gosto do usuário sem comprometer a performance.

---

## 🛠️ Tecnologias e Arquitetura

O core do projeto está sendo desenvolvido focando em desempenho e extensibilidade:

* **C++** (O coracao do ArtexDesktop)
* **lua:** Em breve suporte a linguagens de script leves para customizações rápidas sem necessidade de recompilação

---

## 🧩 Ecossistema do Projeto

O ArtexDesktop funciona como quebra

| Repositório | Descrição | Status |
| :--- | :--- | :---: |
| 🛠️ [Artex Apps](https://github.com/Dimitrof04/ArtexDesktopApps) | Suíte de aplicativos e utilitários auxiliares do ecossistema. | 🛠️ *Manutenção* |
| 🌀 [ArtexDesktop Hyprland](https://github.com/Dimitrof04/ArtexDesktopHyprland) | Configurações, temas e integração específica para o compositor Hyprland (Wayland). | 🚀 *Ativo* |
| 🌐 [ArtexDesktop Gnome](https://github.com/Dimitrof04/ArtexDesktopGnome) | Integração e extensão dedicada ao ambiente GNOME. | 🔒 *Privado* |

---

## 🚀 Instalação e Compilação

> **Nota:** O repositório está em desenvolvimento ativo.

### Pré-requisitos
* Compilador C++ com suporte a **C++17** ou superior (`g++` / `clang`)
* `cmake` ou `make`
* Dependências do sistema (detalhadas nos submódulos)

```bash
# Clone o repositório
git clone [https://github.com/Dimitrof04/ArtexDesktop.git](https://github.com/Dimitrof04/ArtexDesktop.git)

# Acesse o diretório
cd ArtexDesktop

# Exemplo de build padrão
mkdir build && cd build
cmake ..
make
