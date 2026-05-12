# Manual de Usuario
## Sistema de Actualizacion Automatica - Grupo2000

## 1. Descripcion General

El sistema permite:

- Descargar automaticamente datasets desde la plataforma web.
- Procesar y normalizar la informacion.
- Insertar registros nuevos en el Excel maestro.
- Crear automaticamente una hoja destino si no existe.
- Mantener actualizadas las formulas.
- Generar logs de ejecucion.

Objetivo: mantener el Excel maestro actualizado con minima intervencion manual.

## 2. Requisitos

Antes de usar el sistema:

- Python 3 instalado.
- LibreOffice instalado.
- Acceso a internet.
- Archivos Excel maestro existentes (uno por usuario configurado).
- `config.json` completo con credenciales y rutas.

Importante:

- El archivo Excel maestro de cada usuario debe existir.
- La hoja destino de cada dataset ya no necesita existir previamente: el sistema puede crearla automaticamente.

## 3. Instalacion en macOS

### Paso 1 - Ubicar el proyecto

Ejemplo de ruta:

`/Users/usuario/Grupo2000`

### Paso 2 - Configurar credenciales

Editar `config.json` y completar:

- Usuario (`usuarios[].nombre`)
- Contrasena (`usuarios[].password`)
- Ruta completa del Excel maestro por usuario (`usuarios[].maestro_path`)
- Reintentos de login si se quiere sobrescribir el valor por defecto (`web.login_retries`)

Si se configuran multiples usuarios, cada uno debe tener su propio `maestro_path`.

Si `web.login_retries` no se informa, el sistema usa `3` intentos automaticamente ante fallos transitorios de login.

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
- Crea acceso directo en Escritorio solo para ejecucion manual (`~/Desktop/Grupo2000.command`).

## 4. Modos de ejecucion

### macOS

- Manual (visible): `run.command`
- Automatico (headless): `run_auto.command`

En ejecucion manual, al finalizar se anuncia verbalmente:

- Exito: "Grupo 2000 finalizado correctamente"
- Error: "Error en la ejecucion. Revisar log."

En ejecucion automatica:

- No se usa `say`.
- Se escribe `logs/last_run.log`.
- Se escribe `logs/debug.log`.
- Si VoiceOver estaba activo, `run_auto.command` lo restaura al terminar.

### Windows

- Ejecucion manual del ejecutable: `dist\Grupo2000.exe`
- Ejecucion automatica recomendada: `run_auto_windows.bat` desde Programador de tareas
- En modo `auto`, el navegador corre headless
- Si falla un dataset o un usuario puntual, el sistema intenta seguir con el resto

Al finalizar la ejecucion en Windows:

- Se reproduce sonido del sistema.
- Se muestra popup (`MessageBox`) de exito o error.
- El lector de pantalla detecta ese popup automaticamente.

## 5. Ejecucion manual

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

## 6. Programacion automatica en macOS (cron)

Para ejecucion diaria automatica:

1. Abrir Terminal.
2. Ejecutar:

```bash
crontab -e
```

3. Agregar una linea como ejemplo:

```cron
0 8 * * * /bin/bash /Users/usuario/Grupo2000/run_auto.command
```

4. Guardar y verificar:

```bash
crontab -l
```

Importante: usar `run_auto.command` para evitar navegador visible en ejecuciones automaticas.
El script tambien deja un `logs/debug.log` con la fecha de corrida y el codigo de salida.

## 6.1 Programacion automatica en Windows (Programador de tareas)

Para ejecucion diaria automatica:

1. Editar `run_auto_windows.bat` y completar:
   - `APP_DIR`
   - `APP_EXE`
2. Abrir `Programador de tareas`.
3. Crear una tarea nueva.
4. Configurar un desencadenador diario con la hora deseada.
5. En `Acciones`, elegir `Iniciar un programa` y apuntar a `run_auto_windows.bat`.
6. Si se desea correr sin sesion iniciada, configurar la tarea con un usuario que tenga contrasena.

Importante:

- En Windows automatico el sistema corre el navegador en headless.
- `run_auto_windows.bat` escribe `logs\last_run.log` y `logs\debug.log`.
- Si la cuenta local no tiene contrasena, Windows normalmente solo permite `Ejecutar solo cuando el usuario haya iniciado sesion`.

## 7. Logs y seguimiento

Log principal:

`logs/last_run.log`

Log auxiliar de automatizacion:

`logs/debug.log`

Permite revisar:

- Errores
- Pasos ejecutados
- Mensajes de diagnostico
- Datasets sin datos para el rango pedido
- Fallos parciales por dataset o usuario

Si una hoja destino no existe, el log deja trazado:

- Que se uso `fecha_inicial_si_vacio`.
- Que la hoja fue creada automaticamente.
- Que los encabezados se generaron a partir del dataset descargado.

## 7.1 Chequeo/Fix de formato de datasets

Antes de insertar datos en el Excel maestro, el sistema normaliza y valida cada dataset:

- Convierte fechas a formato fecha real.
- Ordena filas por fecha.
- Convierte importes a numerico.
- Registra en log cuantas fechas/importes invalidos detecto.

Esto evita que formatos inconsistentes lleguen al maestro sin control.

## 8. Manejo de Errores

### Error de autenticacion

Mensaje:

`ERROR: Problema de autenticacion. Revise usuario/contrasena en config.json.`

Accion:

1. Revisar usuario/contrasena en `config.json`.
2. Guardar.
3. Ejecutar nuevamente.

Nota: si el problema fue transitorio, el sistema intenta el login automaticamente hasta `3` veces por defecto antes de fallar.

### Sitio no disponible o caido

Mensaje:

`ERROR: La web no responde o esta caida. Revise el archivo de log para mas detalles.`

Accion:

1. Esperar unos minutos.
2. Verificar conectividad a internet.
3. Reintentar la ejecucion.
4. Si persiste, revisar `logs/last_run.log` para identificar si fue timeout o pagina de indisponibilidad.

### Descarga bloqueada por Chrome

Mensaje:

`ERROR: Chrome bloqueo la descarga automatica. Revise el archivo de log para mas detalles.`

Accion:

1. Reintentar la ejecucion.
2. Verificar que Chrome no haya dejado advertencias de descarga peligrosa.
3. Si persiste, reportar el incidente junto con `logs/last_run.log`.

### Rango valido sin datos para exportar

Puede ocurrir que el rango sea valido, incluso de un solo dia, pero que la web todavia no tenga registros disponibles.

En ese caso:

1. El sistema no debe quedar colgado esperando una descarga.
2. Registra en log que no hubo datos para ese rango.
3. Continua con el siguiente dataset o usuario.

Accion recomendada:

1. Revisar `logs/last_run.log`.
2. Esperar a que los registros aparezcan en la web.
3. Ejecutar nuevamente en la siguiente corrida programada o manual.

### LibreOffice no disponible

Se registra en log cuando no se puede convertir `.xls`.

Accion: instalar/verificar LibreOffice y reintentar.

### Excel maestro no encontrado

Mensaje:

`No se encontro el archivo: [ruta]`

Accion: verificar `usuarios[].maestro_path` del usuario que se esta procesando en `config.json`.

### Hoja destino inexistente en el maestro

Si la hoja configurada en `datasets[].hoja_destino` no existe:

1. El sistema no falla por ese motivo.
2. Usa `procesamiento.fecha_inicial_si_vacio` para determinar desde que fecha descargar.
3. Crea la hoja automaticamente al momento de insertar el dataset.
4. Usa como encabezados los nombres de columnas del dataset normalizado.

Esto queda registrado en `logs/last_run.log`.

### Fallo parcial de un dataset o de un usuario

Si un dataset falla pero otros pueden procesarse:

1. El sistema registra cual fue el fallo.
2. Continua con los datasets restantes.
3. No se pierde el trabajo que si pudo completarse.

Si un usuario falla pero hay otros usuarios configurados:

1. El sistema registra el error del usuario afectado.
2. Continua con el siguiente usuario.

### Formulas tipo array en Excel maestro

La ejecucion falla si hay formulas array (`{}`) en columnas donde el sistema debe estirar formulas.

Accion:

1. Abrir Excel maestro.
2. Corregir esas formulas en la ultima fila aplicable.
3. Guardar.
4. Ejecutar nuevamente.

## 9. Recomendaciones

- No editar manualmente las ultimas filas mientras corre el sistema.
- Evitar formulas array en columnas extendibles.
- Revisar periodicamente `logs/last_run.log`.
- Si se usa ejecucion automatica en macOS, revisar tambien `logs/debug.log`.
- Si se usa ejecucion automatica en Windows, revisar tambien `logs/debug.log`.
- Revisar en los logs si hubo fallos parciales aunque la corrida general haya terminado.
- Mantener credenciales actualizadas.
- Tener en cuenta que un unico dia pendiente tambien se procesa; no hace falta esperar a acumular varios dias.
- Si se agrega un dataset nuevo, no es obligatorio crear manualmente la hoja destino antes de la primera corrida.

## 10. Soporte

Ante incidentes:

1. Revisar `logs/last_run.log`.
2. Confirmar requisitos instalados.
3. Reportar el error completo al equipo de soporte.
