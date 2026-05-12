# Documentacion Funcional
## Sistema de Actualizacion Automatica - Grupo2000

## 1. Objetivo del Sistema

Automatizar:

- Descarga de datos desde plataforma web.
- Procesamiento y transformacion de archivos.
- Actualizacion incremental de Excel maestro por usuario.
- Extension de formulas.
- Ejecucion manual y automatica segun sistema operativo.

## 2. Alcance

El sistema:

- Procesa unicamente fechas nuevas respecto del Excel maestro de cada usuario.
- Procesa tambien rangos de un unico dia pendiente (`fecha_desde == fecha_hasta`).
- No sobrescribe registros historicos.
- No sobrescribe ni recrea hojas ya existentes.
- Puede crear automaticamente una hoja destino faltante en el Excel maestro.
- Si la hoja destino no existe o no tiene fechas validas, usa `procesamiento.fecha_inicial_si_vacio` como fecha inicial.
- Replica formulas existentes hacia filas nuevas.
- Tolera fallos parciales por dataset o por usuario, priorizando completar todo lo posible en una misma corrida.

## 3. Componentes

- Entrypoint: `main.py`
- Modulos: `utils/`, `excel/`, `web/`
- Configuracion: `config.json`
- Scripts macOS: `setup_mac.sh`, `run.command`, `run_auto.command`
- Script Windows: `run_auto_windows.bat`
- Ejecutable Windows: `dist\Grupo2000.exe`
- Logs: `logs/last_run.log`

## 4. Modos de ejecucion y comportamiento por plataforma

### 4.1 Parametro de modo

`main.py` acepta:

- `--mode manual`
- `--mode auto`

Si no se especifica, el modo por defecto es `manual`.

### 4.2 Resolucion de visibilidad del navegador

- macOS + `manual`: navegador visible.
- macOS + `auto`: navegador headless.
- Windows + `manual`: navegador visible.
- Windows + `auto`: navegador headless.

Implementacion: deteccion con `platform.system()` y resolucion de `HEADLESS` antes de inicializar Selenium.

### 4.3 Scheduler

- macOS: scheduler por `cron`, apuntando a `run_auto.command`.
- Windows: scheduler por Programador de tareas, apuntando a `run_auto_windows.bat` o directamente al ejecutable si la instalacion ya resuelve rutas y logs.

## 5. Flujo funcional

1. Carga de configuracion (`config.json`).
2. Inicializacion de WebDriver con headless segun modo/plataforma.
3. Iteracion por usuario configurado (`usuarios[]`), usando su `maestro_path`.
4. Login en plataforma con reintentos automaticos configurables (por defecto: `3`).
5. Determinacion incremental de rango de fechas por dataset (contra el maestro del usuario actual).
6. Si la hoja destino no existe, se usa `fecha_inicial_si_vacio` para calcular el rango a descargar.
7. Descarga, lectura, validacion y consolidacion.
8. Chequeo/fix de formato del dataset (normalizacion de fechas/importes y orden por fecha).
9. Si la hoja destino no existe, se crea automaticamente con encabezados tomados del dataset normalizado.
10. Insercion en Excel maestro y estirado de formulas.
11. Logout y cierre de navegador.
12. Limpieza de temporales de descarga.

## 5.2 Tolerancia a fallos parciales

El flujo principal intenta completar la mayor cantidad posible de trabajo en una misma corrida:

- Si falla un dataset de un usuario, el error se registra y se continua con los datasets restantes.
- Si falla un usuario completo, el error se registra y se continua con el siguiente usuario.
- La corrida solo falla globalmente si no se pudo completar correctamente ningun usuario o dataset.

## 5.3 Rango valido sin datos

Cuando `fecha_desde == fecha_hasta`, el rango sigue siendo funcionalmente valido.

Si la web no devuelve registros para ese rango:

- el sistema detecta que no hubo datos para exportar
- no queda esperando indefinidamente una descarga inexistente
- registra el caso en log y continua con el siguiente bloque, dataset o usuario

## 5.1 Normalizacion y validacion de formato de datasets

Antes de insertar en Excel, el sistema aplica un paso de chequeo/fix de formato:

- Convierte la columna fecha a `datetime` con `dayfirst=True` y tolerancia a valores invalidos.
- Marca y contabiliza fechas invalidas en el resumen.
- Ordena el dataset por fecha.
- Convierte columnas de importe a tipo numerico y contabiliza valores invalidos por columna.

Este paso esta implementado en `utils/converter.py` (`normalizar_y_validar_dataset`).

## 6. Manejo global de errores y codigos de salida

`main.py` encapsula el flujo principal y retorna:

- Exit code `0` en exito.
- Exit code `1` en error.

Tipos de error contemplados:

- Autenticacion fallida.
- Sitio no disponible o caido.
- Descarga bloqueada por Chrome.
- Formulas array incompatibles en Excel maestro.
- Errores inesperados.
- Fallos parciales de dataset o usuario registrados para analisis posterior.

Adicionalmente:

- El login reintenta automaticamente ante errores transitorios del sitio.
- Si la plataforma devuelve una pagina de indisponibilidad o no carga a tiempo, el error se clasifica como disponibilidad del sitio y no como error desconocido.
- Si Chrome deja una descarga en estado `Unconfirmed ... .crdownload`, el sistema la identifica como posible bloqueo de seguridad.
- Si la exportacion no inicia y la pagina muestra que no hay registros, el sistema lo trata como ausencia de datos y no como bloqueo.

## 7. Notificaciones de fin de ejecucion

### 7.1 macOS

No se notifica desde `main.py`.
La notificacion manual se realiza en `run.command` mediante `say`, evaluando exit code.

### 7.2 Windows

Desde `main.py` (sin dependencias externas):

- Exito:
  - `winsound.MessageBeep(MB_ICONASTERISK)`
  - `MessageBoxW` informativo: "Proceso finalizado correctamente"
- Error:
  - `winsound.MessageBeep(MB_ICONHAND)`
  - `MessageBoxW` error: "Error en la ejecucion. Revisar log."

Esto mejora accesibilidad para lector de pantalla al usar dialogo del sistema.

## 8. Scripts operativos macOS

### 8.1 `run.command` (manual)

- Autoposiciona con `cd "$(dirname "$0")"`.
- Crea `logs/` si no existe.
- Ejecuta: `.venv/bin/python main.py --mode manual`
- Redirige a `logs/last_run.log`.
- Usa `say` segun exit code.

### 8.2 `run_auto.command` (automatico)

- Resuelve el directorio base desde la ubicacion del script.
- Ejecuta: `.venv/bin/python main.py --mode auto`
- Redirige salida a `logs/last_run.log`.
- Registra trazas basicas en `logs/debug.log`.
- Si VoiceOver estaba activo antes de correr, lo cierra temporalmente y lo reactiva al finalizar.
- Disenado para uso en cron.

## 8.3 Script operativo Windows

### `run_auto_windows.bat` (automatico)

- Usa placeholders configurables para ruta del ejecutable y directorio de logs.
- Valida que el `.exe` exista antes de ejecutar.
- Redirige salida a `logs\last_run.log`.
- Registra fecha, hora y exit code en `logs\debug.log`.
- Disenado para uso con Programador de tareas.

## 9. Configuracion y dependencias

- Python 3
- LibreOffice (conversion de `.xls`)
- Dependencias Python de `requirements.txt`

## 10. Observabilidad

Log principal:

`logs/last_run.log`

Log auxiliar para automatizacion:

`logs/debug.log`

Uso funcional:

- Auditoria de ejecucion.
- Diagnostico de fallos.
- Trazabilidad operativa.
- Confirmacion de uso de `fecha_inicial_si_vacio` cuando falta la hoja destino.
- Confirmacion de creacion automatica de hoja y encabezados.
- Identificacion de datasets sin datos para un rango valido.
- Identificacion de fallos parciales por usuario o dataset.

## 11. Limitaciones conocidas

- Dependencia de estabilidad de plataforma web.
- Dependencia de LibreOffice para conversiones.
- Sensibilidad a cambios estructurales del Excel maestro.
- No soporte de formulas array extendibles en columnas de insercion.
- La deteccion de descarga bloqueada por Chrome se basa en indicios del archivo temporal generado por el navegador.
- Si una hoja nueva se crea automaticamente, los encabezados se toman del dataset descargado y no de una plantilla previa del maestro.

## 12. Evolucion sugerida

- Migrar scheduler de macOS a `launchd` (opcional).
- Canal adicional de alertas (email/Teams).
- Validaciones de integridad adicionales previas a insercion.
