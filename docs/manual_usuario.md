# Manual de Usuario
## Sistema de Actualización Automática - Grupo2000

## 1. Descripción General

El sistema permite:

- Descargar automáticamente datasets desde la plataforma web.
- Procesar y normalizar la información.
- Insertar registros nuevos en el Excel maestro.
- Crear automáticamente una hoja destino si no existe.
- Mantener actualizadas las fórmulas.
- Generar logs de ejecución.

Objetivo: mantener el Excel maestro actualizado con mínima intervención manual.

## 2. Requisitos

Antes de usar el sistema:

- Python 3 instalado.
- LibreOffice instalado.
- Acceso a internet.
- Archivos Excel maestro existentes (uno por usuario configurado).
- `config.json` completo con credenciales y rutas.

Importante:

- El archivo Excel maestro de cada usuario debe existir.
- La hoja destino de cada dataset ya no necesita existir previamente: el sistema puede crearla automáticamente.

## 3. Instalación en macOS

### Paso 1 - Ubicar el proyecto

Ejemplo de ruta:

`/Users/usuario/Grupo2000`

### Paso 2 - Configurar credenciales

Editar `config.json` y completar:

- Usuario (`usuarios[].nombre`)
- Contraseña (`usuarios[].password`)
- Ruta completa del Excel maestro por usuario (`usuarios[].maestro_path`)
- Reintentos de login si se quiere sobrescribir el valor por defecto (`web.login_retries`)

Si se configuran múltiples usuarios, cada uno debe tener su propio `maestro_path`.

Si `web.login_retries` no se informa, el sistema usa `3` intentos automáticamente ante fallos transitorios de login.

### Paso 3 - Ejecutar instalador

Desde la carpeta del proyecto:

```bash
./setup_mac.sh
```

Este proceso:

- Verifica Python.
- Verifica LibreOffice.
- Crea `.venv` si no existe.
- Instala dependencias.
- Da permisos a `run.command` y `run_auto.command`.
- Crea acceso directo en Escritorio solo para ejecución manual (`~/Desktop/Grupo2000.command`).

## 4. Modos de ejecución

### macOS

- Manual (visible): `run.command`
- Automático (headless): `run_auto.command`

En ejecución manual, al finalizar se anuncia verbalmente:

- Éxito: "Grupo 2000 finalizado correctamente"
- Error: "Error en la ejecución. Revisar log."

En ejecución automática:

- No se usa `say`.
- Se escribe `logs/last_run.log`.
- Se escribe `logs/debug.log`.
- Si VoiceOver estaba activo, `run_auto.command` lo restaura al terminar.

### Windows

- Ejecución manual del ejecutable: `dist\Grupo2000.exe`
- No se configura scheduler en Windows dentro del alcance actual.

Al finalizar la ejecución en Windows:

- Se reproduce sonido del sistema.
- Se muestra popup (`MessageBox`) de éxito o error.
- El lector de pantalla detecta ese popup automáticamente.

## 5. Ejecución manual

### macOS

Desde Terminal:

```bash
./run.command
```

O con doble clic en `~/Desktop/Grupo2000.command`.

### Windows

Desde PowerShell o CMD, en la carpeta `dist`:

```powershell
.\Grupo2000.exe
```

## 6. Programación automática en macOS (cron)

Para ejecución diaria automática:

1. Abrir Terminal.
2. Ejecutar:

```bash
crontab -e
```

3. Agregar una línea como ejemplo:

```cron
0 8 * * * /bin/bash /Users/usuario/Grupo2000/run_auto.command
```

4. Guardar y verificar:

```bash
crontab -l
```

Importante: usar `run_auto.command` para evitar navegador visible en ejecuciones automáticas.
El script también deja un `logs/debug.log` con la fecha de corrida y el código de salida.

## 7. Logs y seguimiento

Log principal:

`logs/last_run.log`

Log auxiliar de automatización en macOS:

`logs/debug.log`

Permite revisar:

- Errores
- Pasos ejecutados
- Mensajes de diagnóstico

Si una hoja destino no existe, el log deja trazado:

- Que se usó `fecha_inicial_si_vacio`.
- Que la hoja fue creada automáticamente.
- Que los encabezados se generaron a partir del dataset descargado.

## 7.1 Chequeo/Fix de formato de datasets

Antes de insertar datos en el Excel maestro, el sistema normaliza y valida cada dataset:

- Convierte fechas a formato fecha real.
- Ordena filas por fecha.
- Convierte importes a numérico.
- Registra en log cuántas fechas/importes inválidos detectó.

Esto evita que formatos inconsistentes lleguen al maestro sin control.

## 8. Manejo de Errores

### Error de autenticación

Mensaje:

`ERROR: Problema de autenticación. Revise usuario/contraseña en config.json.`

Acción:

1. Revisar usuario/contraseña en `config.json`.
2. Guardar.
3. Ejecutar nuevamente.

Nota: si el problema fue transitorio, el sistema intenta el login automáticamente hasta `3` veces por defecto antes de fallar.

### Sitio no disponible o caído

Mensaje:

`ERROR: La web no responde o está caída. Revise el archivo de log para más detalles.`

Acción:

1. Esperar unos minutos.
2. Verificar conectividad a internet.
3. Reintentar la ejecución.
4. Si persiste, revisar `logs/last_run.log` para identificar si fue timeout o página de indisponibilidad.

### Descarga bloqueada por Chrome

Mensaje:

`ERROR: Chrome bloqueó la descarga automática. Revise el archivo de log para más detalles.`

Acción:

1. Reintentar la ejecución.
2. Verificar que Chrome no haya dejado advertencias de descarga peligrosa.
3. Si persiste, reportar el incidente junto con `logs/last_run.log`.

### LibreOffice no disponible

Se registra en log cuando no se puede convertir `.xls`.

Acción: instalar/verificar LibreOffice y reintentar.

### Excel maestro no encontrado

Mensaje:

`No se encontró el archivo: [ruta]`

Acción: verificar `usuarios[].maestro_path` del usuario que se está procesando en `config.json`.

### Hoja destino inexistente en el maestro

Si la hoja configurada en `datasets[].hoja_destino` no existe:

1. El sistema no falla por ese motivo.
2. Usa `procesamiento.fecha_inicial_si_vacio` para determinar desde qué fecha descargar.
3. Crea la hoja automáticamente al momento de insertar el dataset.
4. Usa como encabezados los nombres de columnas del dataset normalizado.

Esto queda registrado en `logs/last_run.log`.

### Fórmulas tipo array en Excel maestro

La ejecución falla si hay fórmulas array (`{}`) en columnas donde el sistema debe estirar fórmulas.

Acción:

1. Abrir Excel maestro.
2. Corregir esas fórmulas en la última fila aplicable.
3. Guardar.
4. Ejecutar nuevamente.

## 9. Recomendaciones

- No editar manualmente las últimas filas mientras corre el sistema.
- Evitar fórmulas array en columnas extendibles.
- Revisar periódicamente `logs/last_run.log`.
- Si se usa ejecución automática en macOS, revisar también `logs/debug.log`.
- Mantener credenciales actualizadas.
- Tener en cuenta que un único día pendiente también se procesa; no hace falta esperar a acumular varios días.
- Si se agrega un dataset nuevo, no es obligatorio crear manualmente la hoja destino antes de la primera corrida.

## 10. Soporte

Ante incidentes:

1. Revisar `logs/last_run.log`.
2. Confirmar requisitos instalados.
3. Reportar el error completo al equipo de soporte.
