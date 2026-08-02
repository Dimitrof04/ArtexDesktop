#!/usr/bin/env python3
import fcntl
import json
import os
import subprocess
import sys
import time
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell

    HAS_LAYER_SHELL = True
except (ValueError, ImportError, ModuleNotFoundError) as e:
    print(f"[ShellBar] GtkLayerShell indisponível, seguindo sem ele: {e}")
    HAS_LAYER_SHELL = False

from gi.repository import Gdk, GLib, Gtk

from Modules.ShellBar.styles import CONFIG_PATH, StyleManager, load_config

_LOCK_PATH = "/tmp/shellbar.lock"
_lock_file_handle = None


def ensure_single_instance():
    """Garante que só exista uma única instância do ShellBar em execução."""
    global _lock_file_handle
    _lock_file_handle = open(_LOCK_PATH, "w")
    try:
        fcntl.lockf(_lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[ShellBar] Já existe uma instância em execução. Encerrando.")
        sys.exit(1)
    _lock_file_handle.write(str(os.getpid()))
    _lock_file_handle.flush()


class DesktopBar(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hyprland Python Shell Bar")

        # Provedor global do CSS para atualização dinâmica
        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        if HAS_LAYER_SHELL:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            GtkLayerShell.auto_exclusive_zone_enable(self)

            # Fixar nas bordas: Esquerda, Direita e Topo
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

            # Margens zeradas na LayerShell
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 0)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 0)

        # Configurar transparência no nível da janela GTK
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.last_config_mtime = 0
        self.cfg = {}

        window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(window_box)

        # Barra contínua (Celestia Shell container)
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_box.get_style_context().add_class("bar-container")
        window_box.pack_start(main_box, True, True, 0)

        # Sub-boxes de organização
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        left_box.set_halign(Gtk.Align.START)
        center_box.set_halign(Gtk.Align.CENTER)
        right_box.set_halign(Gtk.Align.END)

        main_box.pack_start(left_box, True, True, 0)
        main_box.set_center_widget(center_box)
        main_box.pack_end(right_box, True, True, 0)

        self.distro_btn = Gtk.Button(label="󰣇")
        self.distro_btn.get_style_context().add_class("arch-btn")
        self.distro_btn.connect("clicked", lambda w: self.run_app("menu"))
        left_box.pack_start(self.distro_btn, False, False, 0)

        self.ws_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=0
        )
        self.ws_box.get_style_context().add_class("workspaces-pill")
        left_box.pack_start(self.ws_box, False, False, 0)

        self.clock_label = Gtk.Label()
        self.clock_label.get_style_context().add_class("clock-pill")

        clock_event_box = Gtk.EventBox()
        clock_event_box.add(self.clock_label)
        clock_event_box.connect(
            "button-press-event",
            lambda w, e: self.run_app("calendar") if e.button == 1 else None,
        )
        center_box.pack_start(clock_event_box, False, False, 0)

        self.audio_btn = Gtk.Button(label="󰕾 100%")
        self.audio_btn.get_style_context().add_class("status-pill")
        self.audio_btn.connect("button-press-event", self.on_audio_click)
        right_box.pack_start(self.audio_btn, False, False, 0)

        self.bt_btn = Gtk.Button(label="")
        self.bt_btn.get_style_context().add_class("status-pill")
        self.bt_btn.connect(
            "clicked",
            lambda w: subprocess.Popen(["~/.config/waybar/BluetoothMenu"]),
        )
        right_box.pack_start(self.bt_btn, False, False, 0)

        self.net_btn = Gtk.Button(label="")
        self.net_btn.get_style_context().add_class("status-pill")
        self.net_btn.connect(
            "clicked",
            lambda w: subprocess.Popen(["~/.config/waybar/NetworkWindow"]),
        )
        right_box.pack_start(self.net_btn, False, False, 0)

        # Carregar configurações e estilos iniciais
        self.reload_config_if_changed()

        GLib.timeout_add(200, self.update_workspaces)
        GLib.timeout_add(1000, self.update_clock)
        GLib.timeout_add(500, self.reload_config_if_changed)

        self.update_clock()
        self.update_workspaces()

    def reload_config_if_changed(self):
        """Atualiza a interface caso a configuração mude em tempo de execução."""
        if os.path.exists(CONFIG_PATH):
            mtime = os.path.getmtime(CONFIG_PATH)
            if mtime != self.last_config_mtime:
                self.last_config_mtime = mtime
                self.cfg = load_config()
                self.apply_styles()
        else:
            if not self.cfg:
                self.cfg = load_config()
                self.apply_styles()
        return True

    def apply_styles(self):
        """Aplica o CSS e força o GTK a redesenhar todos os botões e a barra imediatamente."""
        css = StyleManager.generate_css(self.cfg)
        
        # Recarrega a folha de estilos
        self.css_provider.load_from_data(css.encode())
        
        # Garante vínculo direto com a janela
        self.get_style_context().add_provider(
            self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Força o redesenho da barra inteira e dos botões
        self.reset_style()
        self.queue_draw()

    def run_app(self, app_key):
        """Executa um comando configurado no Desktop.conf."""
        cmd = self.cfg.get(app_key)
        if cmd:
            subprocess.Popen(cmd, shell=True)

    def update_clock(self):
        """Atualiza o texto do relógio central."""
        now = time.strftime("%d/%m 󰸗   %H:%M")
        self.clock_label.set_text(now)
        return True

    def update_workspaces(self):
        """Obtém os workspaces ativos do Hyprland e recria os indicadores dinamicamente."""
        try:
            ws_out = json.loads(
                subprocess.check_output(["hyprctl", "workspaces", "-j"])
            )
            act_out = json.loads(
                subprocess.check_output(["hyprctl", "activeworkspace", "-j"])
            )
            active_id = act_out.get("id", 1)

            for child in self.ws_box.get_children():
                self.ws_box.remove(child)

            ws_list = sorted(ws_out, key=lambda x: x["id"])
            for ws in ws_list:
                ws_id = ws["id"]
                label = ""
                btn = Gtk.Button(label=label)
                btn.get_style_context().add_class("ws-btn")

                if ws_id == active_id:
                    btn.get_style_context().add_class("active")

                btn.connect(
                    "clicked",
                    lambda w, i=ws_id: subprocess.run(
                        ["hyprctl", "dispatch", "workspace", str(i)]
                    ),
                )
                self.ws_box.pack_start(btn, False, False, 0)

            self.ws_box.show_all()
        except Exception:
            pass
        return True

    def on_audio_click(self, widget, event):
        """Gerencia cliques do mouse no controle de áudio."""
        if event.button == 1:
            subprocess.Popen(["pavucontrol"])
        elif event.button == 3:
            subprocess.Popen(
                ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"]
            )


if __name__ == "__main__":
    ensure_single_instance()
    win = DesktopBar()
    win.connect("destroy", Gtk.main_quit)
    win.set_default_size(-1, 32)
    win.show_all()
    Gtk.main()