<div align="center">

<img src="engrane.ico" width="100" height="100" alt="Icono original de engranaje de J.D DEV Windows Setup" />

# ⚙️ J.D DEV — Windows Setup

**Herramienta de personalización y configuración inicial de Windows 10/11**

Una interfaz gráfica para aplicar ajustes elegidos por el usuario, con confirmaciones y comprobación de puntos de restauración.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Interfaz-Tkinter-2D774B)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows11&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-Administraci%C3%B3n-5391FE?logo=powershell&logoColor=white)
![PyInstaller](https://img.shields.io/badge/Empaquetado-PyInstaller-245CC7)
![Versión](https://img.shields.io/badge/Versi%C3%B3n-v0.1.0%20preliminar-E39B20)
[![Pruebas](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup/actions/workflows/checks.yml/badge.svg)](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup/actions/workflows/checks.yml)

[📦 **Descargar v0.1.0**](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup/releases/tag/v0.1.0) · [💻 **Código fuente**](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup) · [✅ **Pruebas**](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup/actions/workflows/checks.yml)

**J.D DEV · Jimmy Díaz**

</div>

---

> [!WARNING]
> **Versión preliminar de pruebas.** Los controles de seguridad tienen pruebas automatizadas con operaciones simuladas. Los ajustes del sistema aún necesitan validación en máquinas virtuales y distintas versiones de Windows. El ejecutable no está firmado digitalmente.

## 🛠️ Tecnologías utilizadas

| Área | Herramienta |
| --- | --- |
| **Lenguaje principal** | Python |
| **Interfaz gráfica** | Tkinter |
| **Automatización del sistema** | PowerShell, servicios y Registro de Windows |
| **Empaquetado** | PyInstaller (ejecutable para Windows) |
| **Pruebas** | `unittest`, GitHub Actions (Windows) |
| **Sistema operativo** | Windows 10 y Windows 11 |

## 💻 Cuándo utilizarla

Se recomienda utilizarla **después de formatear e instalar Windows**, una vez instalados los controladores y completadas las actualizaciones. Revisa las opciones y decide cuáles necesitas; la configuración completa combina cambios de apariencia, rendimiento y telemetría.

El programa no formatea, no reinstala Windows y no sustituye la instalación de controladores. Los efectos de cada ajuste dependen de la versión, edición y políticas del sistema. Prueba primero en una máquina virtual.

## 🎯 Objetivo

J.D DEV Windows Setup reúne en una sola aplicación opciones de apariencia y ajustes habituales tras la instalación de Windows. No formatea equipos, no instala controladores y **no ejecuta cambios automáticamente al abrirse**.

## ✨ Funcionalidades principales

- Iconos del escritorio, espaciado, tema oscuro, Peek y opciones de barra de tareas.
- Ajustes de rendimiento y opciones de telemetría mediante Registro y servicios.
- Registro de operaciones, información del equipo y progreso.
- Punto de restauración previo a la ejecución de ajustes.
- Ejecución manual: abrir la aplicación no inicia la configuración.
- Confirmación previa para la configuración completa y para opciones individuales.
- El proceso se detiene si no se puede crear el punto de restauración.
- El programa no reinicia Windows automáticamente; el usuario decide cuándo hacerlo desde Windows.

Algunos cambios reinician Explorer y pueden cerrar sus ventanas. Guarda tu trabajo antes de aplicar ajustes. El punto de restauración depende de Protección del sistema y no equivale a una copia completa de tus archivos. [Restaurar sistema: Microsoft](https://support.microsoft.com/en-us/windows/experience/backup-recovery/system-restore).

## 📦 Descargar la versión preliminar

[Descargar la versión preliminar para Windows](https://github.com/jimmyfabian26-sys/jd-dev-windows-setup/releases).

## 🚀 Ejecutar desde el código fuente

Requiere Windows, Python 3.10 o posterior con Tkinter y permisos de administrador para aplicar los cambios.

```powershell
python ConfiguracionAutomatica.py
```

No requiere dependencias externas para ejecutarse. La aplicación solicita elevación si es necesaria. La ruta puede contener espacios.

## 🏗️ Compilar el ejecutable

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --uac-admin --name J.D-DEV-Windows-Setup --icon engrane.ico ConfiguracionAutomatica.py
```

La salida se genera en `dist/J.D-DEV-Windows-Setup.exe`. No se incluyen ejecutables antiguos en este repositorio. El binario publicado no cuenta con firma de código.

## 📁 Estructura del proyecto

```text
ConfiguracionAutomatica.py  Aplicación e interfaz J.D DEV
engrane.ico                Icono del ejecutable
test_setup.py              Pruebas con acciones del sistema simuladas
.gitignore                 Excluye binarios y archivos locales
```

## ✅ Pruebas automáticas

```powershell
python -m unittest discover -p test_setup.py -v
```

Las pruebas verifican cancelación, ejecución única, bloqueo si falla la restauración, ausencia de reinicio automático y marca. Simulan las operaciones del sistema: no modifican el Registro, los servicios ni el equipo.

## ⚠️ Estado del proyecto y próximas mejoras

Código público para revisión y mejora. La interfaz y los controles de ejecución se han actualizado; los ajustes del sistema requieren validación en máquinas virtuales y distintas compilaciones de Windows antes de una release estable.

Pendiente: exportar valores previos del Registro, permitir selección granular en la configuración completa y registrar un resultado por operación para informar fallos parciales con mayor claridad.

## 📄 Autor y condiciones de uso

**J.D DEV · Jimmy Díaz** · [GitHub](https://github.com/jimmyfabian26-sys).

No se ha añadido una licencia de uso: la visibilidad pública del repositorio permite revisarlo, pero no otorga por sí sola una licencia de redistribución.
