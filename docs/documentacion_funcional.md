# Documentación Funcional
## Sistema de Actualización Automática - Grupo2000

## 1. Objetivo del Sistema

Automatizar:

- Descarga de datos desde plataforma web.
- Procesamiento y transformación de archivos.
- Actualización incremental de Excel maestro.
- Extensión de fórmulas.
- Ejecución manual y automática según sistema operativo.

## 2. Alcance

El sistema:

- Procesa únicamente fechas nuevas respecto del Excel maestro.
- No sobrescribe registros históricos.
- No altera estructura de hojas existentes.
- No crea hojas nuevas automáticamente.
- Replica fórmulas existentes hacia filas nuevas.

## 3. Componentes

- Entrypoint: `main.py`
- Módulos: `utils/`, `excel/`, `web/`
- Configuración: `config.json`
- Scripts macOS: `setup_mac.sh`, `run.command`, `run_auto.command`
- Ejecutable Windows: `dist\Grupo2000.exe`
- Logs: `logs/last_run.log`

## 4. Modos de ejecución y comportamiento por plataforma

### 4.1 Parámetro de modo

`main.py` acepta:

- `--mode manual`
- `--mode auto`

Si no se especifica, el modo por defecto es `manual`.

### 4.2 Resolución de visibilidad del navegador

- macOS + `manual`: navegador visible.
- macOS + `auto`: navegador headless.
- Windows: siempre visible (modo headless no aplicado).

Implementación: detección con `platform.system()` y resolución de `HEADLESS` antes de inicializar Selenium.

### 4.3 Scheduler

- macOS: scheduler por `cron`, apuntando a `run_auto.command`.
- Windows: fuera de alcance del proyecto actual (solo ejecución manual).

## 5. Flujo funcional

1. Carga de configuración (`config.json`).
2. Inicialización de WebDriver con headless según modo/plataforma.
3. Login en plataforma.
4. Determinación incremental de rango de fechas por dataset.
5. Descarga, lectura, validación y consolidación.
6. Inserción en Excel maestro y estirado de fórmulas.
7. Logout y cierre de navegador.
8. Limpieza de temporales de descarga.

## 6. Manejo global de errores y códigos de salida

`main.py` encapsula el flujo principal y retorna:

- Exit code `0` en éxito.
- Exit code `1` en error.

Tipos de error contemplados:

- Autenticación fallida.
- Fórmulas array incompatibles en Excel maestro.
- Errores inesperados.

## 7. Notificaciones de fin de ejecución

### 7.1 macOS

No se notifica desde `main.py`.
La notificación se realiza en scripts `.command` mediante `say`, evaluando exit code.

### 7.2 Windows

Desde `main.py` (sin dependencias externas):

- Éxito:
  - `winsound.MessageBeep(MB_ICONASTERISK)`
  - `MessageBoxW` informativo: "Proceso finalizado correctamente"
- Error:
  - `winsound.MessageBeep(MB_ICONHAND)`
  - `MessageBoxW` error: "Error en la ejecución. Revisar log."

Esto mejora accesibilidad para lector de pantalla al usar diálogo del sistema.

## 8. Scripts operativos macOS

### 8.1 `run.command` (manual)

- Autoposiciona con `cd "$(dirname "$0")"`.
- Crea `logs/` si no existe.
- Ejecuta: `.venv/bin/python main.py --mode manual`
- Redirige a `logs/last_run.log`.
- Usa `say` según exit code.

### 8.2 `run_auto.command` (automático)

- Misma estructura operativa.
- Ejecuta: `.venv/bin/python main.py --mode auto`
- Diseñado para uso en cron.

### 8.3 `setup_mac.sh`

- Mantiene creación de `.venv` e instalación de dependencias.
- Da permisos de ejecución a `run.command` y `run_auto.command`.
- Crea symlink en Escritorio solo a `run.command`.

## 9. Configuración y dependencias

- Python 3
- LibreOffice (conversión de `.xls`)
- Dependencias Python de `requirements.txt`

## 10. Observabilidad

Log principal:

`logs/last_run.log`

Uso funcional:

- Auditoría de ejecución.
- Diagnóstico de fallos.
- Trazabilidad operativa.

## 11. Limitaciones conocidas

- Dependencia de estabilidad de plataforma web.
- Dependencia de LibreOffice para conversiones.
- Sensibilidad a cambios estructurales del Excel maestro.
- No soporte de fórmulas array extendibles en columnas de inserción.
- En Windows no se incluye scheduler en esta versión.

## 12. Evolución sugerida

- Migrar scheduler de macOS a `launchd` (opcional).
- Canal adicional de alertas (email/Teams).
- Validaciones de integridad adicionales previas a inserción.