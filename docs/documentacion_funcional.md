# Documentación Funcional
## Sistema de Actualización Automática - Grupo2000

## 1. Objetivo del Sistema

Automatizar:

- Descarga de datos desde plataforma web.
- Procesamiento y transformación de archivos.
- Actualización incremental de Excel maestro por usuario.
- Extensión de fórmulas.
- Ejecución manual y automática según sistema operativo.

## 2. Alcance

El sistema:

- Procesa únicamente fechas nuevas respecto del Excel maestro de cada usuario.
- Procesa también rangos de un único día pendiente (`fecha_desde == fecha_hasta`).
- No sobrescribe registros históricos.
- No sobrescribe ni recrea hojas ya existentes.
- Puede crear automáticamente una hoja destino faltante en el Excel maestro.
- Si la hoja destino no existe o no tiene fechas válidas, usa `procesamiento.fecha_inicial_si_vacio` como fecha inicial.
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
3. Iteración por usuario configurado (`usuarios[]`), usando su `maestro_path`.
4. Login en plataforma con reintentos automáticos configurables (por defecto: `3`).
5. Determinación incremental de rango de fechas por dataset (contra el maestro del usuario actual).
6. Si la hoja destino no existe, se usa `fecha_inicial_si_vacio` para calcular el rango a descargar.
7. Descarga, lectura, validación y consolidación.
8. Chequeo/fix de formato del dataset (normalización de fechas/importes y orden por fecha).
9. Si la hoja destino no existe, se crea automáticamente con encabezados tomados del dataset normalizado.
10. Inserción en Excel maestro y estirado de fórmulas.
11. Logout y cierre de navegador.
12. Limpieza de temporales de descarga.

## 5.1 Normalización y validación de formato de datasets

Antes de insertar en Excel, el sistema aplica un paso de chequeo/fix de formato:

- Convierte la columna fecha a `datetime` con `dayfirst=True` y tolerancia a valores inválidos.
- Marca y contabiliza fechas inválidas en el resumen.
- Ordena el dataset por fecha.
- Convierte columnas de importe a tipo numérico y contabiliza valores inválidos por columna.

Este paso está implementado en `utils/converter.py` (`normalizar_y_validar_dataset`).

## 6. Manejo global de errores y códigos de salida

`main.py` encapsula el flujo principal y retorna:

- Exit code `0` en éxito.
- Exit code `1` en error.

Tipos de error contemplados:

- Autenticación fallida.
- Sitio no disponible o caído.
- Descarga bloqueada por Chrome.
- Fórmulas array incompatibles en Excel maestro.
- Errores inesperados.

Adicionalmente:

- El login reintenta automáticamente ante errores transitorios del sitio.
- Si la plataforma devuelve una página de indisponibilidad o no carga a tiempo, el error se clasifica como disponibilidad del sitio y no como error desconocido.
- Si Chrome deja una descarga en estado `Unconfirmed ... .crdownload`, el sistema la identifica como posible bloqueo de seguridad.

## 7. Notificaciones de fin de ejecución

### 7.1 macOS

No se notifica desde `main.py`.
La notificación manual se realiza en `run.command` mediante `say`, evaluando exit code.

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

- Resuelve el directorio base desde la ubicación del script.
- Ejecuta: `.venv/bin/python main.py --mode auto`
- Redirige salida a `logs/last_run.log`.
- Registra trazas básicas en `logs/debug.log`.
- Si VoiceOver estaba activo antes de correr, lo cierra temporalmente y lo reactiva al finalizar.
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

Log auxiliar para automatización macOS:

`logs/debug.log`

Uso funcional:

- Auditoría de ejecución.
- Diagnóstico de fallos.
- Trazabilidad operativa.
- Confirmación de uso de `fecha_inicial_si_vacio` cuando falta la hoja destino.
- Confirmación de creación automática de hoja y encabezados.

## 11. Limitaciones conocidas

- Dependencia de estabilidad de plataforma web.
- Dependencia de LibreOffice para conversiones.
- Sensibilidad a cambios estructurales del Excel maestro.
- No soporte de fórmulas array extendibles en columnas de inserción.
- En Windows no se incluye scheduler en esta versión.
- La detección de descarga bloqueada por Chrome se basa en indicios del archivo temporal generado por el navegador.
- Si una hoja nueva se crea automáticamente, los encabezados se toman del dataset descargado y no de una plantilla previa del maestro.

## 12. Evolución sugerida

- Migrar scheduler de macOS a `launchd` (opcional).
- Canal adicional de alertas (email/Teams).
- Validaciones de integridad adicionales previas a inserción.
