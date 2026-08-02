#!/usr/bin/env python3

import argparse
import fcntl
import os
import signal
import subprocess
import sys
from Modules.theme_sync import set_system_theme

# --- 1. GARANTE O DIRETÓRIO CORRETO ---
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)


# Caminhos dos Scripts
StartMenuPath = os.path.expanduser("~/.local/share/ArtexDesktop/StartMenu.py")
DektopConfigMenuPath = os.path.expanduser(
    "~/.local/share/ArtexDesktop/DektopConfigMenu.py"
)
ShellBarPath = os.path.expanduser("~/.local/share/ArtexDesktop/ShellBar.py")

# Mapeamento de serviços para PIDs e Locks
SERVICES = {
    "Desktop": {
        "path": DektopConfigMenuPath,
        "lock": "DesktopConfig",
        "name": "DesktopConfigMenu.py",
    },
    "ShellBar": {
        "path": ShellBarPath,
        "lock": "ShellBar",
        "name": "ShellBar.py",
    },
    "StartMenu": {
        "path": StartMenuPath,
        "lock": "StartMenu",
        "name": "StartMenu.py",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ArtexDesktop",
        description="Thanks for using :3",
        epilog="Criado por Dimitrof04",
    )

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s v0.2"
    )

    # 1. Módulos / Alvos principais
    parser.add_argument(
        "--StartMenu", action="store_true", help="Target: Menu Launcher"
    )

    parser.add_argument(
        "--ShellBar", action="store_true", help="Target: ShellBar / Taskbar"
    )

    parser.add_argument(
        "--Desktop", action="store_true", help="Target: Desktop Config"
    )

    # 2. Sub-comandos de Gerenciamento de Ação
    parser.add_argument(
        "-i", "--init", action="store_true", help="Iniciar o serviço selecionado"
    )

    parser.add_argument(
        "-k", "--kill", action="store_true", help="Matar o serviço selecionado"
    )

    parser.add_argument(
        "-r",
        "--restart",
        action="store_true",
        help="Reiniciar o serviço selecionado",
    )

    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Verificar status do serviço",
    )

    # 3. Alteração de Tema
    parser.add_argument(
        "--theme",
        type=str,
        help="Altera o tema do sistema (opções: Light, Dark)",
    )

    return parser.parse_args()


# --- TRAVA E PID MANAGEMENT ---
def check_menu_lock(menu_name: str):
    lock_file_path = f"/tmp/ArtexDesktop_{menu_name}.lock"
    lock_file = open(lock_file_path, "w")
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        return None


def get_service_pid(script_name: str):
    """Procura pelo PID do processo usando pgrep."""
    try:
        pid_bytes = subprocess.check_output(["pgrep", "-f", script_name])
        pids = pid_bytes.decode().strip().split("\n")
        # Retorna o PID filtrando o próprio CLI se necessário
        for pid in pids:
            if int(pid) != os.getpid():
                return int(pid)
    except subprocess.CalledProcessError:
        return None
    return None


def get_active_workspace():
    """Captura o workspace ativo do Hyprland."""
    try:
        ws_out = subprocess.check_output(
            ["hyprctl", "activeworkspace", "-j"]
        ).decode()
        import json

        ws_data = json.loads(ws_out)
        return f"Workspace{ws_data.get('id', '1')}"
    except Exception:
        return "Workspace Unknown"


# --- CONTROLE DE SERVIÇOS ---
def kill_service(service_info):
    pid = get_service_pid(service_info["name"])
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 Serviço {service_info['name']} encerrado (PID: {pid}).")
            return True
        except ProcessLookupError:
            print("⚠️ Processo não localizado.")
    else:
        print(f"⚠️ {service_info['name']} não está rodando.")
    return False


def start_service(service_info):
    lock = check_menu_lock(service_info["lock"])
    if not lock:
        print(f"⚠️ {service_info['name']} já está em execução!")
        return

    # Inicia como processo independente em segundo plano
    subprocess.Popen(["python3", service_info["path"]])
    print(f"🚀 {service_info['name']} iniciado com sucesso.")


def status_service(service_info):
    pid = get_service_pid(service_info["name"])
    if pid:
        ws = get_active_workspace()
        print(f'Running : "{ws}"')
    else:
        print("not Running")


def handle_action(service_key, args):
    service = SERVICES[service_key]

    if args.kill:
        kill_service(service)
    # CORRIGIDO: Removido 'args.r' pois 'args.restart' já trata tanto '-r' quanto '--restart'
    elif args.restart:
        print(f"🔄 Reiniciando {service_key}...")
        kill_service(service)
        start_service(service)
    elif args.status:
        status_service(service)
    elif args.init or not (args.kill or args.restart or args.status):
        # Se usar -i ou chamar apenas a flag do menu (ex: ArtexDesktop --Desktop)
        start_service(service)


def main():
    args = parse_args()

    # 1. Trata o argumento de Tema
    if args.theme:
        tema_formatado = args.theme.capitalize()
        if tema_formatado in ["Dark", "Light"]:
            set_system_theme(tema_formatado, None)
        else:
            print(
                f"⚠️ Tema '{args.theme}' inválido! Use apenas 'Dark' ou 'Light'."
            )

    # 2. Trata comandos direcionados aos alvos especificos
    elif args.Desktop:
        handle_action("Desktop", args)

    elif args.ShellBar:
        handle_action("ShellBar", args)

    elif args.StartMenu:
        handle_action("StartMenu", args)

    # 3. Caso o usuário passe apenas -r, -k, -i, -s sem especificar o alvo (Aplica na ShellBar por padrão)
    elif args.restart or args.kill or args.init or args.status:
        handle_action("ShellBar", args)

    else:
        print("Nothing executed. Try using -h or --help")


if __name__ == "__main__":
    main()