# J.D DEV · Windows Setup

Herramienta gráfica para personalizar la apariencia y aplicar opciones de configuración de Windows 10/11 después de reinstalar el sistema.

**Tecnologías:** Python, Tkinter, Registro de Windows y PowerShell.

## Cuándo usarla

Se recomienda utilizarla **después de formatear e instalar Windows**, una vez instalados los controladores y completadas las actualizaciones. Revisa las opciones y decide cuáles necesitas; la configuración completa combina cambios de apariencia, rendimiento y telemetría.

El programa no formatea, no reinstala Windows y no sustituye la instalación de controladores. Los efectos de cada ajuste dependen de la versión, edición y políticas del sistema. Prueba primero en una máquina virtual.

## Funciones

- Iconos del escritorio, espaciado, tema oscuro, Peek y opciones de barra de tareas.
- Ajustes de rendimiento y opciones de telemetría mediante Registro y servicios.
- Registro de operaciones, información del equipo y progreso.
- Punto de restauración previo a la ejecución de ajustes.
- Ejecución manual: abrir la aplicación no inicia la configuración.
- Confirmación previa para la configuración completa y para opciones individuales.
- El proceso se detiene si no se puede crear el punto de restauración.
- El programa no reinicia Windows automáticamente; el usuario decide cuándo hacerlo desde Windows.

Algunos cambios reinician Explorer y pueden cerrar sus ventanas. Guarda tu trabajo antes de aplicar ajustes. El punto de restauración depende de Protección del sistema y no equivale a una copia completa de tus archivos. [Restaurar sistema: Microsoft](https://support.microsoft.com/en-us/windows/experience/backup-recovery/system-restore).

## Ejecutar el código

Requiere Windows, Python 3.10 o posterior con Tkinter y permisos de administrador para aplicar los cambios.

```powershell
python ConfiguracionAutomatica.py
```

No requiere dependencias externas para ejecutarse. La aplicación solicita elevación si es necesaria. La ruta puede contener espacios.

## Crear el ejecutable

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --uac-admin --name J.D-DEV-Windows-Setup --icon engrane.ico ConfiguracionAutomatica.py
```

La salida se genera en `dist/J.D-DEV-Windows-Setup.exe`. No se incluyen ejecutables antiguos en este repositorio. El binario publicado no cuenta con firma de código.

## Estructura

```text
ConfiguracionAutomatica.py  Aplicación e interfaz J.D DEV
engrane.ico                Icono del ejecutable
test_setup.py              Pruebas con acciones del sistema simuladas
.gitignore                 Excluye binarios y archivos locales
```

## Pruebas

```powershell
python -m unittest discover -p test_setup.py -v
```

Las pruebas verifican cancelación, ejecución única, bloqueo si falla la restauración, ausencia de reinicio automático y marca. Simulan las operaciones del sistema: no modifican el Registro, los servicios ni el equipo.

## Estado

Código público para revisión y mejora. La interfaz y los controles de ejecución se han actualizado; los ajustes del sistema requieren validación en máquinas virtuales y distintas compilaciones de Windows antes de una release estable.

Pendiente: exportar valores previos del Registro, permitir selección granular en la configuración completa y registrar un resultado por operación para informar fallos parciales con mayor claridad.

## Autor

**J.D DEV · Jimmy Díaz** · [GitHub](https://github.com/jimmyfabian26-sys).

No se ha añadido una licencia de uso: la visibilidad pública del repositorio permite revisarlo, pero no otorga por sí sola una licencia de redistribución.
