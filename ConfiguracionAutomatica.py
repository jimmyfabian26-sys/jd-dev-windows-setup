#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
J.D DEV - Windows Setup v0.2.0 Classic Edition
Aplicación Python para optimización de Windows 10/11
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
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
        self.root.title("J.D DEV - Configuración Inteligente · Classic Edition")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.ui_scale = 0.9 if screen_w <= 1366 else 1.0
        window_w = min(1160, max(760, screen_w - 70))
        window_h = min(760, max(540, screen_h - 110))
        self.window_size = f"{window_w}x{window_h}"

        self.root.geometry(self.window_size)
        self.root.configure(bg='#040b18')
        self.root.resizable(True, True)
        self.root.minsize(760, 540)
        self.running = False
        self.countdown_remaining = 5
        self.countdown_state = "ready"
        self.countdown_job = None

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
        else:
            self.begin_countdown()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def setup_styles(self):
        self.colors = {
            'bg': '#040b18', 'fg': '#75ecff', 'accent': '#081c32',
            'text': '#e0ecfa', 'warning': '#ff9cbe', 'success': '#00e5ff',
            'border': '#17d9f3', 'yellow': '#ffe34d',
        }
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('Cyber.Horizontal.TProgressbar', troughcolor='#071a2d',
                        background='#00d9ff', bordercolor='#123d60',
                        lightcolor='#00d9ff', darkcolor='#087ba3', thickness=5)

    def create_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'],
                              highlightthickness=1, highlightbackground='#0b91b2')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.main_frame = main_frame
        self.create_header(main_frame)
        self.create_countdown_panel(main_frame)
        self.create_system_info(main_frame)

        footer = tk.Frame(main_frame, bg='#081c32', highlightthickness=1,
                          highlightbackground='#147ca5', padx=9, pady=3)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(3, 8))
        self.status_label = tk.Label(
            footer, text="Listo. Esperando inicio automático…", bg='#081c32',
            fg='#e0ecfa', font=('Segoe UI', 10), anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(footer, variable=self.progress_var,
            maximum=100, mode='determinate', style='Cyber.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(2, 0))
        self.create_usage_notice(main_frame)

        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 2))
        content_frame.grid_columnconfigure(0, weight=47, uniform='panel')
        content_frame.grid_columnconfigure(1, weight=53, uniform='panel')
        content_frame.grid_rowconfigure(0, weight=1)
        self.create_menu_panel(content_frame)
        self.create_console_panel(content_frame)

    def create_usage_notice(self, parent):
        tk.Label(parent, text="RECOMENDADO DESPUÉS DE REINSTALAR WINDOWS · Instala controladores y actualizaciones primero.",
                 bg=self.colors['bg'], fg='#82a7bc', font=('Segoe UI', 8),
                 anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(1, 2))

    def neon_frame(self, parent, title, height=0, border='#16cde8', fill='#081c32'):
        """Canvas decorativo; los controles del interior siguen siendo widgets nativos."""
        panel = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0,
                          bd=0, height=height or 80, width=1)
        body = tk.Frame(panel, bg=fill, bd=0)
        top = 29 if title else 9
        body.place(x=10, y=top, relwidth=1, width=-20, relheight=1, height=-top-8)

        def paint(event):
            w, h = event.width, event.height
            if w < 30 or h < 35:
                return
            panel.delete('decoration')
            cut = 10
            points = (2, cut+2, cut+2, 2, w-cut-2, 2, w-2, cut+2,
                      w-2, h-cut-2, w-cut-2, h-2, cut+2, h-2, 2, h-cut-2)
            panel.create_polygon(points, fill=fill, outline='#103752',
                                 width=5, tags='decoration')
            panel.create_polygon(points, fill=fill, outline=border,
                                 width=1, tags='decoration')
            if title:
                panel.create_text(15, 14, text=title, anchor='w',
                                  font=('Segoe UI', 10, 'bold'), fill='#75ecff',
                                  tags='decoration')
                panel.create_line(5, 25, w-5, 25, fill='#14577a', tags='decoration')
            panel.tag_lower('decoration')

        panel.bind('<Configure>', paint)
        return panel, body

    def create_header(self, parent):
        """Paisaje synthwave generado con Canvas; el logotipo es texto Unicode."""
        header = tk.Canvas(parent, bg='#030a1b', height=146,
                           highlightthickness=0, bd=0)
        header.pack(fill=tk.X, padx=3)
        self.header_canvas = header
        # Half-blocks encode two square pixels per text row. Keep fixed spacing.
        glyphs = (
            "   ▀▀██      ██▀▀█▄        ██▀▀█▄   ██▀▀▀▀▀  ██   ██",
            "     ██      ██   ██       ██   ██  ██▄▄▄▄   ██   ██",
            "██   ██  ▄▄  ██  ▄█▀       ██  ▄█▀  ██        ▀█▄█▀ ",
            " ▀▀▀▀▀   ▀▀  ▀▀▀▀▀         ▀▀▀▀▀    ▀▀▀▀▀▀▀     ▀   ",
        )
        ascii_logo = "\n".join(glyphs)
        self.logo_font = tkfont.Font(family='Consolas', size=-15, weight='bold')
        os_name = 'Windows 11' if self.is_windows_11 else 'Windows 10'

        def center_logo(event):
            w, h = event.width, event.height
            header.delete('all')
            # Cielo nocturno, estrellas, sol pixelado, montañas y cuadrícula.
            colors = ('#03091a', '#050d25', '#09102c', '#111638', '#181c43')
            for i, color in enumerate(colors):
                y0 = round(i*h/len(colors))
                y1 = round((i+1)*h/len(colors))
                header.create_rectangle(0, y0, w, y1, fill=color, outline='')
            for i in range(42):
                x = (i*137+23) % max(1,w)
                y = (i*31+7) % max(1,int(h*0.65))
                c = '#275276' if i%3 else '#49a8c4'
                header.create_rectangle(x,y,x+1+(i%2),y+1,fill=c,outline='')
            sx, sy, r = int(w*0.135), int(h*0.46), int(h*0.29)
            for dy in range(-r,r+1,3):
                half = int(max(0,r*r-dy*dy)**0.5)
                if dy > 0 and (dy//3)%3 == 2:
                    continue
                col = '#00d9ee' if dy<0 else ('#4392d9' if dy<r/2 else '#a65acf')
                header.create_rectangle(sx-half,sy+dy,sx+half,sy+dy+3,fill=col,outline='')
            horizon = int(h*0.82)
            header.create_polygon(0,horizon, w*.08,h*.58,w*.15,h*.76,
                w*.22,h*.51,w*.32,h*.80,w*.45,h*.66,w*.54,h*.79,
                w*.68,h*.58,w*.76,h*.76,w*.84,h*.49,w*.94,h*.72,w,h*.64,w,h,
                0,h,fill='#07162f',outline='#142c51')
            for side in (0,1):
                for i in range(7):
                    x = 8+i*17 if side==0 else w-21-i*17
                    bw = 11+i%3*3
                    bh = 13+(i*19+side*9)%48
                    top = horizon-bh
                    header.create_rectangle(x,top,x+bw,horizon,fill='#040b1c',outline='#112c4d')
                    for yy in range(top+5,horizon-3,8):
                        header.create_rectangle(x+3,yy,x+5,yy+3,
                            fill='#008fbf' if (i+yy)%3 else '#b54ace',outline='')
            header.create_rectangle(0,horizon,w,h,fill='#071126',outline='')
            for i in range(13):
                header.create_line(w/2+(i-6)*w*.027,horizon,
                    w/2+(i-6)*w*.23,h,fill='#15568a')
            for i in (0,3,7,13,22):
                header.create_line(0,horizon+i,w,horizon+i,fill='#15568a')
            # Sombra azul desplazada, texto sólido cian y subtítulo.
            size = max(10, min(30, int(w/32)))
            self.logo_font.configure(size=-size)
            while size > 10 and (self.logo_font.metrics("linespace") * len(glyphs) > h-35
                                  or self.logo_font.measure(glyphs[0]) > w*0.69):
                size -= 1
                self.logo_font.configure(size=-size)
            logo_h = self.logo_font.metrics('linespace') * len(glyphs)
            logo_y = max(4, (h-30-logo_h)//2)
            header.create_text(w/2+3,logo_y+3,text=ascii_logo,font=self.logo_font,
                               fill='#1356a6',anchor='n',justify=tk.LEFT)
            header.create_text(w/2,logo_y,text=ascii_logo,font=self.logo_font,
                               fill='#16e8ff',anchor='n',justify=tk.LEFT)
            subtitle = f"CONFIGURACIÓN INTELIGENTE · {os_name} Detectado"
            header.create_rectangle(w*.20,h-27,w*.80,h-4,fill='#050c1d',outline='')
            header.create_text(w/2,h-16,text=subtitle,font=('Segoe UI',11,'bold'),fill='#75ecff')
            header.create_line(0,h-1,w,h-1,fill='#1197b9')

        header.bind('<Configure>',center_logo)

    def create_countdown_panel(self, parent):
        panel, body = self.neon_frame(parent, '', height=91,
                                      border='#ff518b', fill='#39142e')
        panel.pack(fill=tk.X, padx=15, pady=(5, 4))
        self.countdown_label = tk.Label(body, text="Inicio automático en 00:05",
            bg='#39142e', fg='#6ff0ff', font=('Consolas', 16, 'bold'))
        self.countdown_label.pack(pady=(0, 2))
        for relx in (0.045, 0.955):
            tk.Label(body, text="╱╱╱", bg='#39142e', fg='#a82a66',
                     font=('Consolas', 23, 'bold')).place(relx=relx, rely=0.5, anchor='center')
        controls = tk.Frame(body, bg='#39142e')
        controls.pack()
        self.countdown_pause_btn = tk.Button(controls, text="Ⅱ  Pausar",
            command=self.toggle_countdown, bg='#0b2943', fg='#91f5ff',
            activebackground='#164f6e', activeforeground='white', disabledforeground='#8aa1aa',
            highlightthickness=1, highlightbackground='#36dfff', highlightcolor='#36dfff',
            relief=tk.FLAT, bd=0, padx=19, pady=3, font=('Segoe UI',10,'bold'), cursor='hand2')
        self.countdown_pause_btn.pack(side=tk.LEFT, padx=5)
        self.countdown_cancel_btn = tk.Button(controls, text="×  Cancelar",
            command=self.cancel_countdown, bg='#551a3b', fg='#ffb1cd',
            activebackground='#82305a', activeforeground='white', disabledforeground='#aa879b',
            highlightthickness=1, highlightbackground='#ff689e', highlightcolor='#ff689e',
            relief=tk.FLAT, bd=0, padx=19, pady=3, font=('Segoe UI',10,'bold'), cursor='hand2')
        self.countdown_cancel_btn.pack(side=tk.LEFT, padx=5)

    def begin_countdown(self):
        if self.countdown_state != "ready":
            return
        self.countdown_state = "running"
        self.countdown_job = self.root.after(1000, self.countdown_tick)

    def countdown_tick(self):
        self.countdown_job = None
        if self.countdown_state != "running":
            return
        self.countdown_remaining -= 1
        self.countdown_label.config(text=f"Inicio automático en 00:{self.countdown_remaining:02d}")
        if self.countdown_remaining <= 0:
            self.countdown_state = "finished"
            self.countdown_pause_btn.config(state='disabled')
            self.countdown_cancel_btn.config(state='disabled')
            self.countdown_label.config(text="Esperando confirmación")
            self.config_completa()
            self.countdown_label.config(text="Modo manual")
        else:
            self.countdown_job = self.root.after(1000, self.countdown_tick)

    def toggle_countdown(self):
        if self.countdown_state == "running":
            if self.countdown_job is not None:
                self.root.after_cancel(self.countdown_job)
                self.countdown_job = None
            self.countdown_state = "paused"
            self.countdown_label.config(text=f"Pausado · 00:{self.countdown_remaining:02d}")
            self.countdown_pause_btn.config(text="▶  Reanudar")
        elif self.countdown_state == "paused":
            self.countdown_state = "running"
            self.countdown_pause_btn.config(text="Ⅱ  Pausar")
            self.countdown_label.config(text=f"Inicio automático en 00:{self.countdown_remaining:02d}")
            self.countdown_job = self.root.after(1000, self.countdown_tick)

    def cancel_countdown(self):
        if getattr(self, 'countdown_state', None) not in ("ready", "running", "paused"):
            return
        if self.countdown_job is not None:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        self.countdown_state = "cancelled"
        self.countdown_label.config(text="Inicio automático cancelado · Modo manual")
        self.safe_log("Inicio automático cancelado por el usuario.")
        self.countdown_pause_btn.config(state='disabled')
        self.countdown_cancel_btn.config(state='disabled')

    def close_window(self):
        if self.running:
            messagebox.showinfo("J.D DEV", "Espera a que termine la configuración en curso.")
            return
        self.cancel_countdown()
        self.root.destroy()

    def create_system_info(self, parent):
        panel, body = self.neon_frame(parent, '▣  Información del Sistema', height=68)
        panel.pack(fill=tk.X, padx=10, pady=(4, 3))
        info_text = (
            f"Windows: {self.system_info.get('version', 'Desconocido')}  |  "
            f"Build: {self.system_info.get('build', 'N/A')}  |  "
            f"CPU: {self.system_info.get('cpu', 'Desconocido')}  |  "
            f"Hilos: {self.system_info.get('threads', 'N/A')}  |  "
            f"Admin: {'Sí' if self.is_admin else 'No'}"
        )
        info_label = tk.Label(body, text=info_text, bg='#081c32', fg='#e0ecfa',
                              font=('Segoe UI', 9), anchor=tk.W, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
        body.bind('<Configure>', lambda event: info_label.config(wraplength=max(100,event.width-8)))

    def create_menu_panel(self, parent):
        self.advanced_visible = False

        panel, menu_frame = self.neon_frame(parent, '⚙  Panel de Configuración')
        panel.grid(row=0, column=0, sticky='nsew', padx=(0,5))

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

        self._menu_button(menu_frame, "3. SALIR", self.close_window, '#ff6b6b')

    def create_console_panel(self, parent):
        panel, console_frame = self.neon_frame(parent, '>_  Registro de Actividad')
        panel.grid(row=0, column=1, sticky='nsew', padx=(5,0))
        self.console = scrolledtext.ScrolledText(
            console_frame, bg='#02060d', fg='#35ff6b', insertbackground='#35ff6b',
            font=('Consolas', 10), wrap=tk.WORD, state=tk.DISABLED,
            padx=9, pady=8, relief=tk.FLAT, bd=0, highlightthickness=1,
            highlightbackground='#1688a8', highlightcolor='#16d0ee')
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
        self.cancel_countdown()
        if self.running:
            messagebox.showinfo("J.D DEV", "Ya hay una configuración en curso.")
            return
        if not messagebox.askyesno(
            "J.D DEV · Aplicar configuración",
            "Se modificarán apariencia, Registro, opciones de rendimiento y servicios de telemetría. "
            "La optimización actual incluye cambios de arranque y desactivación de UAC (reduce la seguridad). "
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
        self.cancel_countdown()
        if self.running:
            messagebox.showinfo("J.D DEV", "Espera a que termine la configuración en curso.")
            return
        if not messagebox.askyesno("J.D DEV · Aplicar ajuste",
                                  "Esta opción cambiará la configuración de Windows y puede reiniciar Explorer. "
                                  "La opción de rendimiento modifica el arranque y desactiva UAC (reduce la seguridad). "
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

        self.root.update_idletasks()
        popup_h = self.advanced_popup.winfo_reqheight()
        y = ry + bh + 2
        if y + popup_h > self.root.winfo_height():
            y = max(0, ry - popup_h - 2)
        self.advanced_popup.place(x=rx, y=y, width=bw)
        self.advanced_popup.lift()
        self.btn_advanced.config(text="2. Configuración AVANZADA ▲")
        self.advanced_visible = True

    def bind_close_advanced(self):
        self.root.bind("<Button-1>", self._close_if_outside)

    def _close_if_outside(self, event):
        if not self.advanced_visible:
            return
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if widget in (self.advanced_popup, self.btn_advanced):
                return
            widget = getattr(widget, 'master', None)
        self.toggle_advanced()

    def _menu_button(self, parent, text, command, color):
        border = tk.Frame(parent, bg='#15cce9', padx=1, pady=1)
        border.pack(fill=tk.X, pady=4)
        btn = tk.Button(border, text=text, command=command,
            bg='#0a2945', fg=color, activebackground='#174c6d',
            activeforeground=color, font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT, bd=0, padx=8, pady=8, cursor='hand2')
        btn.pack(fill=tk.BOTH, expand=True)
        btn.bind('<Enter>', lambda event: btn.config(bg='#174c6d'))
        btn.bind('<Leave>', lambda event: btn.config(bg='#0a2945', fg=color))
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
