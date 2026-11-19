#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
J.D DEV - Configuración Inteligente v4.0
Aplicación Python para optimización de Windows 10/11
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import logging
import threading
import winreg
import ctypes
import time
from datetime import datetime
from pathlib import Path

# Configuración de logging
LOG_DIR = Path(os.environ.get('TEMP', '.'))
LOG_FILE = LOG_DIR / "JD_DEV_Windows.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class JDDevWindowsSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("J.D DEV - Configuración Inteligente")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if screen_w <= 1366:
            self.ui_scale = 0.85
            self.window_size = "820x580"
        elif screen_w <= 1600:
            self.ui_scale = 0.95
            self.window_size = "880x620"
        else:
            self.ui_scale = 1.0
            self.window_size = "900x640"

        self.root.geometry(self.window_size)
        self.root.tk.call('tk', 'scaling', self.ui_scale)
        self.root.configure(bg='#0a192f')
        self.root.resizable(False, False)
        self.running = False

        # Variables de estado
        self.is_admin = self.check_admin()
        self.system_info = self.get_system_info()
        self.backup_created = False
        self.is_windows_11 = self.check_windows_11()

        # Estilos
        self.setup_styles()

        # UI
        self.create_ui()
        self.bind_close_advanced()
        logging.info(f"Aplicación iniciada - Windows 11: {self.is_windows_11}")
        if not self.is_admin:
            self.request_admin()

    def setup_styles(self):
        """Configurar estilos modernos"""
        self.colors = {
            'bg': '#0a192f',
            'fg': '#64ffda',
            'accent': '#112240',
            'text': '#ccd6f6',
            'warning': '#ff6b6b',
            'success': '#00d9ff'
        }

        style = ttk.Style()
        style.theme_use('clam')

        style.configure(
            'Custom.TButton',
            background=self.colors['accent'],
            foreground=self.colors['fg'],
            font=('Segoe UI', 12, 'bold'),
            padding=10
        )

        style.configure(
            'Custom.TFrame',
            background=self.colors['bg']
        )

    def create_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.main_frame = main_frame

        self.create_header(main_frame)
        self.create_usage_notice(main_frame)
        self.create_system_info(main_frame)

        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        self.create_menu_panel(content_frame)
        self.create_console_panel(content_frame)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=860,
            mode='determinate'
        )
        self.progress.pack(pady=10)

        self.status_label = tk.Label(
            main_frame,
            text="Listo",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Consolas', 9),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)

    def create_usage_notice(self, parent):
        notice = tk.Frame(parent, bg=self.colors['accent'], padx=14, pady=10)
        notice.pack(fill=tk.X, pady=(0, 12))
        tk.Label(notice, text="RECOMENDADO DESPUÉS DE REINSTALAR WINDOWS",
                 bg=self.colors['accent'], fg=self.colors['fg'],
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        tk.Label(notice, text="Instala controladores y actualizaciones primero. Elige los ajustes antes de aplicarlos.",
                 bg=self.colors['accent'], fg=self.colors['text'],
                 font=('Segoe UI', 10), wraplength=740, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 0))

    def create_header(self, parent):
        """Crear header con logo"""
        header = tk.Frame(parent, bg=self.colors['bg'])
        header.pack(fill=tk.X, pady=(0, 20))

        logo_label = tk.Label(
            header, text="J.D DEV", bg=self.colors['bg'],
            fg=self.colors['success'], font=('Segoe UI', int(34 * self.ui_scale), 'bold')
        )
        logo_label.pack()

        subtitle = tk.Label(
            header,
            text=f"WINDOWS SETUP · {'Windows 11' if self.is_windows_11 else 'Windows 10'} Detectado",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Segoe UI', 12)
        )
        subtitle.pack()

    def create_system_info(self, parent):
        """Mostrar información del sistema"""
        info_frame = tk.LabelFrame(
            parent,
            text="Información del Sistema",
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            font=('Segoe UI', 12, 'bold'),
            padx=10,
            pady=5
        )
        info_frame.pack(fill=tk.X, pady=10)

        info_text = (
            f"Windows: {self.system_info.get('version', 'Desconocido')} | "
            f"Build: {self.system_info.get('build', 'N/A')} | "
            f"CPU: {self.system_info.get('cpu', 'Desconocido')} | "
            f"Hilos: {self.system_info.get('threads', 'N/A')} | "
            f"Admin: {'Sí' if self.is_admin else 'No'}"
        )

        info_label = tk.Label(
            info_frame,
            text=info_text,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=('Consolas', 12)
        )
        info_label.pack(anchor=tk.W)

    def create_menu_panel(self, parent):
        self.advanced_visible = False

        menu_frame = tk.LabelFrame(
            parent,
            text="Panel de Configuración",
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            font=('Segoe UI', int(12 * self.ui_scale), 'bold'),
            padx=10,
            pady=10,
            width=360
        )
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        menu_frame.pack_propagate(False)

        self._menu_button(
            menu_frame,
            "1. Configuración COMPLETA",
            self.config_completa,
            '#00d9ff'
        )

        self.btn_advanced = self._menu_button(
            menu_frame,
            "2. Configuración AVANZADA ▼",
            lambda e=None: self.toggle_advanced(),
            '#ffd700'
        )

        self.advanced_popup = tk.Frame(
            self.root,
            bg="#0b1625",
            bd=3,
            relief=tk.RAISED
        )
        self.advanced_popup.config(highlightthickness=1, highlightbackground="#ffd700")

        self.adv_canvas = tk.Canvas(
            self.advanced_popup,
            bg="#0b1625",
            highlightthickness=0,
            height=140
        )
        self.adv_scroll = tk.Scrollbar(
            self.advanced_popup,
            orient="vertical",
            command=self.adv_canvas.yview
        )
        self.adv_canvas.configure(yscrollcommand=self.adv_scroll.set)

        self.adv_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.adv_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.adv_inner = tk.Frame(self.adv_canvas, bg="#0b1625")
        self.adv_canvas.create_window((0, 0), window=self.adv_inner, anchor="nw")
        self.adv_inner.bind("<Configure>", lambda e: self.adv_canvas.configure(scrollregion=self.adv_canvas.bbox("all")))

        self._bind_mousewheel(self.adv_canvas)
        self._bind_mousewheel(self.adv_inner)
        self.create_advanced_options(self.adv_inner)
        self.advanced_popup.place_forget()

        self._menu_button(menu_frame, "3. SALIR", self.root.quit, '#ff6b6b')

    def create_console_panel(self, parent):
        """Panel de consola/log"""
        console_frame = tk.LabelFrame(
            parent,
            text="Registro de Actividad",
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            font=('Segoe UI', 12, 'bold'),
            width=450,
            padx=10,
            pady=10
        )
        console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        console_frame.pack_propagate(False)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 12),
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, message, level="info"):
        """Agregar mensaje desde el hilo principal a la consola y al registro."""
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, lambda m=message, l=level: self.log(m, l))
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"

        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, full_message + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

        if level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        else:
            logging.info(message)

        self.status_label.config(text=message)

    def check_admin(self):
        """Verificar privilegios de administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def request_admin(self):
        """Solicitar elevación de privilegios"""
        if not self.is_admin:
            self.log("Solicitando privilegios de administrador...", "warning")
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, subprocess.list2cmdline(sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv), None, 1
                )
                sys.exit(0)
            except Exception as e:
                messagebox.showerror(
                    "Error de Permisos",
                    "No se pudieron obtener privilegios de administrador.\n"
                    "Por favor, ejecute la aplicación como Administrador."
                )
                sys.exit(1)

    def check_windows_11(self):
        """Detectar si es Windows 11"""
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'CurrentBuildNumber'],
                capture_output=True, text=True
            )
            if "CurrentBuildNumber" in result.stdout:
                build = int(result.stdout.split()[-1].strip())
                return build >= 22000
        except:
            pass
        return False

    def get_system_info(self):
        """Obtener información del sistema"""
        info = {}
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'DisplayVersion'],
                capture_output=True, text=True
            )
            if "DisplayVersion" in result.stdout:
                info['version'] = result.stdout.split()[-1].strip()

            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'CurrentBuildNumber'],
                capture_output=True, text=True
            )
            if "CurrentBuildNumber" in result.stdout:
                info['build'] = result.stdout.split()[-1].strip()

            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', '(Get-CimInstance Win32_Processor).Name'],
                capture_output=True, text=True
            )
            info['cpu'] = result.stdout.strip() if result.stdout else "Desconocido"

            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 '(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors'],
                capture_output=True, text=True
            )
            info['threads'] = result.stdout.strip() if result.stdout else os.cpu_count()

        except Exception as e:
            logging.error(f"Error obteniendo info del sistema: {e}")
            info['threads'] = os.cpu_count()

        return info

    def detect_disk_type(self):
        """Detectar tipo de disco principal"""
        try:
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', 'Get-PhysicalDisk | Select MediaType'],
                capture_output=True, text=True
            )
            output = result.stdout.lower()
            if "ssd" in output:
                return "SSD"
            elif "hdd" in output:
                return "HDD"
            return "UNKNOWN"
        except Exception as e:
            logging.error(f"Error detectando disco: {e}")
            return "UNKNOWN"

    def run_command(self, command, shell=True, check=True):
        """Ejecutar comando con manejo de errores"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if check and result.returncode != 0:
                self.log(f"Error en comando: {command}", "error")
                return False
            return True
        except Exception as e:
            self.log(f"Excepción ejecutando comando: {e}", "error")
            return False

    def set_registry(self, key_path, value_name, value_type, value_data, description=""):
        """Modificar registro de Windows"""
        try:
            if key_path.startswith("HKCU"):
                root = winreg.HKEY_CURRENT_USER
                subkey = key_path[5:]
            elif key_path.startswith("HKLM"):
                root = winreg.HKEY_LOCAL_MACHINE
                subkey = key_path[5:]
            else:
                raise ValueError("Hive de registro no soportado")

            key = winreg.CreateKey(root, subkey)

            type_map = {
                "REG_DWORD": winreg.REG_DWORD,
                "REG_SZ": winreg.REG_SZ,
                "REG_BINARY": winreg.REG_BINARY,
                "REG_QWORD": winreg.REG_QWORD
            }

            reg_type = type_map.get(value_type, winreg.REG_SZ)
            if reg_type == winreg.REG_BINARY and isinstance(value_data, str):
                value_data = bytes.fromhex(value_data)

            winreg.SetValueEx(key, value_name, 0, reg_type, value_data)
            winreg.CloseKey(key)

            self.log(f"[OK] {description or value_name}")
            return True

        except PermissionError:
            self.log(f"[ERROR] Permisos insuficientes: {description}", "error")
            return False
        except Exception as e:
            self.log(f"[ERROR] {description}: {e}", "error")
            return False

    def refresh_desktop_metrics(self):
        """Forzar actualización de métricas de escritorio"""
        SPI_SETICONMETRICS = 0x002D
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETICONMETRICS,
            0,
            None,
            0x01 | 0x02
        )

    def crear_restauracion(self):
        """Crear punto de restauración del sistema"""
        if self.backup_created:
            self.log("Usando el punto de restauración creado en esta sesión.")
            return True
        self.log("Creando punto de restauración...")

        fecha = datetime.now().strftime("%Y%m%d")
        descripcion = f"JD_DEV_Backup_{fecha}"

        try:
            cmd = f'''
            $description = "{descripcion}"
            Checkpoint-Computer -Description $description -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
            Write-Output "OK"
            '''

            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', cmd],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                self.log("[OK] Punto de restauración creado")
                self.backup_created = True
                return True
            else:
                raise Exception(result.stderr)

        except Exception as e:
            self.log(f"[X] Error punto de restauración: {e}", "error")
            self.backup_created = False
            return False

    def apply_registry_batch(self, items):
        for key, val, typ, data, desc in items:
            self.set_registry(key, val, typ, data, desc)

    def aplicar_iconos_clasicos(self):
        desktop_icons = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
            "{59031a47-3f72-44a7-89c5-5595fe6b30ee}", "REG_DWORD", 0, "Usuario"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
            "{20D04FE0-3AEA-1069-A2D8-08002B30309D}", "REG_DWORD", 0, "Este equipo"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
            "{645FF040-5081-101B-9F08-00AA002F954E}", "REG_DWORD", 0, "Papelera"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
            "{5399E694-6CE5-4D6C-8FCE-1D8870FDCBA0}", "REG_DWORD", 0, "Panel de control"),
        ]
        self.apply_registry_batch(desktop_icons)
        self.refresh_desktop_metrics()

    def aplicar_iconos_escritorio(self):
        desktop_ui = [
            ("HKCU\\Control Panel\\Desktop\\WindowMetrics",
            "IconSpacing", "REG_SZ", "-1125", "Espaciado horizontal iconos"),
            ("HKCU\\Control Panel\\Desktop\\WindowMetrics",
            "IconVerticalSpacing", "REG_SZ", "-1125", "Espaciado vertical iconos"),
            ("HKCU\\Software\\Microsoft\\Windows\\Shell\\Bags\\1\\Desktop",
            "IconSize", "REG_DWORD", 32, "Tamaño iconos escritorio"),
        ]
        self.apply_registry_batch(desktop_ui)

    def aplicar_peek(self):
        peek_keys = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "DisablePreviewDesktop", "REG_DWORD", 0, "Usar Vistazo (Peek)"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "EnablePeek", "REG_DWORD", 1, "Enable Peek"),
        ]
        self.apply_registry_batch(peek_keys)

    def aplicar_modo_oscuro(self):
        dark_mode_keys = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            "SystemUsesLightTheme", "REG_DWORD", 0, "Modo oscuro sistema"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            "AppsUseLightTheme", "REG_DWORD", 0, "Modo oscuro apps"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            "EnableTransparency", "REG_DWORD", 1, "Transparencia"),
        ]
        self.apply_registry_batch(dark_mode_keys)

    def aplicar_barra_tareas(self):
        taskbar_keys = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "ShowTaskViewButton", "REG_DWORD", 0, "Ocultar Vista de Tareas"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "ShowCopilotButton", "REG_DWORD", 0, "Ocultar Copilot"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "TaskbarMn", "REG_DWORD", 0, "Ocultar Chat"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search",
            "SearchboxTaskbarMode", "REG_DWORD", 1, "Búsqueda solo icono"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            "TaskbarDa", "REG_DWORD", 0, "Ocultar Widgets"),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Feeds",
            "EnableFeeds", "REG_DWORD", 0, "Noticias y clima"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Feeds",
            "ShellFeedsTaskbarViewMode", "REG_DWORD", 2, "Vista de feeds"),
        ]

        if self.is_windows_11:
            taskbar_keys.append(
                ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                "TaskbarAl", "REG_DWORD", 0, "Barra alineada izquierda (Win11)")
            )

        self.apply_registry_batch(taskbar_keys)

    def config_apariencia(self, silent=False):
        """Configurar apariencia del sistema - Windows 10/11"""
        if not silent:
            self.log("Iniciando configuración de apariencia...")
            self.progress_var.set(0)

        self.log("[1/5] Activando iconos clásicos del escritorio...")
        self.aplicar_iconos_clasicos()
        if not silent:
            self.progress_var.set(20)

        self.log("[2/5] Optimizando iconos del escritorio...")
        self.aplicar_iconos_escritorio()
        if not silent:
            self.progress_var.set(40)

        self.log("[3/5] Configurando Vistazo (Peek)...")
        self.aplicar_peek()
        if not silent:
            self.progress_var.set(60)

        self.log("[4/5] Activando modo oscuro...")
        self.aplicar_modo_oscuro()
        if not silent:
            self.progress_var.set(80)

        self.log("[5/5] Configurando barra de tareas...")
        self.aplicar_barra_tareas()
        if not silent:
            self.progress_var.set(100)
            self.progress_var.set(0)
        return True

    def config_rendimiento(self, silent=False):
        """Configurar rendimiento del sistema"""
        if not silent:
            self.log("Iniciando optimización de rendimiento...")
            self.progress_var.set(0)

        threads = self.system_info.get('threads', 4)

        # 1. Optimización de CPU
        self.log("[1/5] Analizando hardware...")
        self.log(f"    Procesador: {self.system_info.get('cpu', 'Desconocido')}")
        self.log(f"    Hilos: {threads}")

        if not silent:
            self.progress_var.set(20)

        # 2. BCDEDIT
        self.log("[2/5] Optimizando arranque...")
        bcd_commands = [
            f"bcdedit /set {{current}} numproc {threads}",
            "bcdedit /set {current} bootux disabled",
            "bcdedit /set {current} quietboot on",
            "bcdedit /timeout 10"
        ]

        for cmd in bcd_commands:
            self.run_command(cmd, check=False)

        if not silent:
            self.progress_var.set(40)

        # 3. Desactivar UAC
        self.log("[3/5] Desactivando UAC...")
        self.log("ADVERTENCIA: UAC desactivado", "warning")

        uac_keys = [
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
             "EnableLUA", "REG_DWORD", 0, "UAC principal"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
             "ConsentPromptBehaviorAdmin", "REG_DWORD", 0, "Comportamiento UAC"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
             "PromptOnSecureDesktop", "REG_DWORD", 0, "Escritorio seguro UAC"),
        ]

        for key, val, typ, data, desc in uac_keys:
            self.set_registry(key, val, typ, data, desc)

        if not silent:
            self.progress_var.set(60)

        # 4. Efectos visuales
        self.log("[4/5] Configurando efectos visuales...")
        visual_keys = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects",
             "VisualFXSetting", "REG_DWORD", 3, "Efectos visuales rendimiento"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
             "TaskbarAnimations", "REG_DWORD", 0, "Animaciones barra"),
            ("HKCU\\Control Panel\\Desktop\\WindowMetrics",
             "MinAnimate", "REG_SZ", "0", "Animación minimizar"),
            ("HKCU\\Control Panel\\Desktop",
             "UserPreferencesMask", "REG_BINARY", "9012038010000000", "Preferencias visuales"),
        ]

        for key, val, typ, data, desc in visual_keys:
            self.set_registry(key, val, typ, data, desc)

        if not silent:
            self.progress_var.set(80)

        # 5. Servicios según disco
        disk_type = self.detect_disk_type()
        self.log(f"[5/5] Ajustando servicios ({disk_type})...")

        if disk_type == "HDD":
            services = [("SysMain", "disabled"), ("WSearch", "disabled")]
        else:
            services = [("SysMain", "manual"), ("WSearch", "manual")]

        for service, start_type in services:
            self.run_command(f"sc config {service} start= {start_type}", check=False)

        if not silent:
            self.progress_var.set(100)
            self.progress_var.set(0)
        return True

    def desactivar_telemetria(self):
        """Desactivar telemetría y seguimiento"""
        self.log("Desactivando telemetría...")

        telemetry_keys = [
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection",
             "AllowTelemetry", "REG_DWORD", 0, "Telemetría"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection",
             "AllowTelemetry", "REG_DWORD", 0, "Telemetría usuario"),
        ]

        for key, val, typ, data, desc in telemetry_keys:
            self.set_registry(key, val, typ, data, desc)

        services = [("DiagTrack", "disabled"), ("dmwappushservice", "disabled")]
        for service, start_type in services:
            self.run_command(f"sc config {service} start= {start_type}", check=False)

        self.log("[OK] Telemetría desactivada")

    def config_completa(self):
        """La configuración completa solo empieza tras una elección explícita."""
        if self.running:
            messagebox.showinfo("J.D DEV", "Ya hay una configuración en curso.")
            return
        if not messagebox.askyesno(
            "J.D DEV · Aplicar configuración",
            "Se modificarán apariencia, Registro, opciones de rendimiento y servicios de telemetría. "
            "También se reiniciará Explorer. Guarda tu trabajo antes de continuar.\n\n"
            "Se intentará crear un punto de restauración; si falla, se detendrá el proceso.\n\n"
            "¿Quieres aplicar la configuración completa?",
            default='no', parent=self.root
        ):
            return
        self.running = True
        self.progress_var.set(0)
        self.status_label.config(text="Aplicando configuración…")
        threading.Thread(target=self.config_completa_thread, daemon=True).start()

    def config_completa_thread(self):
        completed = False
        try:
            self.safe_log("=== J.D DEV · INICIANDO CONFIGURACIÓN ===")
            if not self.crear_restauracion():
                self.safe_log("Proceso detenido: activa Protección del sistema y vuelve a intentar.", "error")
                return
            self.safe_progress(15)
            self.config_rendimiento(silent=True)
            self.safe_progress(40)
            self.desactivar_telemetria()
            self.safe_progress(65)
            self.config_apariencia(silent=True)
            self.safe_progress(85)
            self.restart_explorer_with_delay(3)
            self.safe_progress(100)
            self.safe_log("=== J.D DEV · CONFIGURACIÓN FINALIZADA ===")
            self.safe_log("Revisa el registro. Reinicia Windows manualmente cuando te convenga.")
            completed = True
        except Exception as e:
            self.safe_log(f"Error durante la configuración: {e}", "error")
        finally:
            self.root.after(0, lambda ok=completed: self.configuration_finished(ok))

    def configuration_finished(self, completed):
        self.running = False
        if completed:
            messagebox.showinfo("J.D DEV · Proceso finalizado",
                                "El proceso ha terminado. Revisa el registro para detectar operaciones fallidas.\n\n"
                                "Puedes reiniciar Windows manualmente para completar los cambios.", parent=self.root)
        else:
            messagebox.showwarning("J.D DEV · Proceso detenido", "Revisa el registro antes de volver a intentar.", parent=self.root)

    def run_and_collapse(self, func):
        if self.running:
            messagebox.showinfo("J.D DEV", "Espera a que termine la configuración en curso.")
            return
        if not messagebox.askyesno("J.D DEV · Aplicar ajuste",
                                  "Esta opción cambiará la configuración de Windows y puede reiniciar Explorer. "
                                  "Guarda tu trabajo antes de continuar. ¿Quieres aplicarla?", default='no', parent=self.root):
            return
        if not self.crear_restauracion():
            messagebox.showwarning("J.D DEV", "No se pudo crear el punto de restauración. El ajuste no se aplicó.", parent=self.root)
            return
        func()
        if self.advanced_visible:
            self.toggle_advanced()

    def create_advanced_options(self, parent):
        options = [
            (
                "A",
                "Iconos del escritorio clásicos",
                lambda: self.run_and_collapse(self.aplicar_iconos_clasicos)
            ),
            (
                "B",
                "Modo oscuro completo",
                lambda: self.run_and_collapse(self.aplicar_modo_oscuro)
            ),
            (
                "C",
                "Habilitar Usar Vistazo (Peek)",
                lambda: self.run_and_collapse(self.aplicar_peek)
            ),
            (
                "D",
                "Barra de tareas minimalista",
                lambda: self.run_and_collapse(self.aplicar_barra_tareas)
            ),
            (
                "E",
                "Optimizar CPU y arranque",
                lambda: self.run_and_collapse(self.config_rendimiento)
            ),
            (
                "F",
                "Desactivar Telemetría",
                lambda: self.run_and_collapse(self.desactivar_telemetria)
            ),
            (
                "G",
                "Aplicar Apariencia Completa",
                lambda: self.run_and_collapse(self.config_apariencia)
            ),
            (
                "H",
                "Reiniciar Explorer",
                lambda: self.run_and_collapse(
                    lambda: self.restart_explorer_with_delay(5)
                )
            ),
        ]

        for letter, text, command in options:
            btn = tk.Button(
                parent,
                text=f"[{letter}] {text}",
                command=command,
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                font=('Segoe UI', 12, 'bold'),
                relief=tk.FLAT,
                padx=10,
                pady=4,
                anchor='w',
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=12, pady=2)

    def toggle_advanced(self):
        if self.advanced_popup.winfo_ismapped():
            self.advanced_popup.place_forget()
            self.btn_advanced.config(text="2. Configuración AVANZADA ▼")
            self.advanced_visible = False
            return

        bx = self.btn_advanced.winfo_rootx()
        by = self.btn_advanced.winfo_rooty()
        bh = self.btn_advanced.winfo_height()
        bw = self.btn_advanced.winfo_width()

        rx = bx - self.root.winfo_rootx()
        ry = by - self.root.winfo_rooty()

        self.advanced_popup.place(x=rx, y=ry + bh + 2, width=bw)
        self.advanced_popup.lift()
        self.btn_advanced.config(text="2. Configuración AVANZADA ▲")
        self.advanced_visible = True

    def bind_close_advanced(self):
        self.root.bind("<Button-1>", self._close_if_outside)

    def _close_if_outside(self, event):
        if not self.advanced_visible:
            return
        if not self.advanced_popup.winfo_containing(event.x_root, event.y_root):
            self.toggle_advanced()

    def _menu_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors['bg'],
            fg=color,
            activebackground=color,
            activeforeground=self.colors['bg'],
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor='hand2'
        )
        btn.pack(fill=tk.X, pady=4)

        btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=c, fg=self.colors['bg']))
        btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['bg'], fg=self.colors['fg']))

        return btn

    def restart_explorer_with_delay(self, delay=5):
        """Reiniciar Explorer con delay específico"""
        self.safe_log(f"Reiniciando Explorer en {delay}s...")
        self.run_command("taskkill /f /im explorer.exe", check=False)
        time.sleep(delay)
        self.run_command("start explorer.exe", check=False)
        time.sleep(2)
        self.safe_log("[OK] Explorer reiniciado")

    def safe_log(self, msg, level="info"):
        self.root.after(0, lambda: self.log(msg, level))

    def safe_progress(self, value):
        self.root.after(0, lambda: self.progress_var.set(value))

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", self._on_mousewheel))
        widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self.adv_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def main():
    if os.name != 'nt':
        print("Esta aplicación solo funciona en Windows.")
        sys.exit(1)

    root = tk.Tk()
    app = JDDevWindowsSetup(root)
    root.mainloop()

if __name__ == "__main__":
    main()
