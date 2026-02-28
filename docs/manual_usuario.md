# Manual de Usuario
## Sistema de Actualización Automática - Grupo2000

## 1. Descripción General

El sistema permite:

- Descargar automáticamente datasets desde la plataforma web.
- Procesar y normalizar la información.
- Insertar registros nuevos en el Excel maestro.
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

## 3. Instalación en macOS

### Paso 1 - Ubicar el proyecto

Ejemplo de ruta:

`/Users/usuario/Grupo2000`

### Paso 2 - Configurar credenciales

Editar `config.json` y completar:

- Usuario (`usuarios[].nombre`)
- Contraseña (`usuarios[].password`)
- Ruta completa del Excel maestro por usuario (`usuarios[].maestro_path`)

Si se configuran múltiples usuarios, cada uno debe tener su propio `maestro_path`.

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

En ambos casos, al finalizar se anuncia verbalmente:

- Éxito: "Grupo 2000 finalizado correctamente"
- Error: "Error en la ejecución. Revisar log."

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

## 7. Logs y seguimiento

Log principal:

`logs/last_run.log`

Permite revisar:

- Errores
- Pasos ejecutados
- Mensajes de diagnóstico

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

### LibreOffice no disponible

Se registra en log cuando no se puede convertir `.xls`.

Acción: instalar/verificar LibreOffice y reintentar.

### Excel maestro no encontrado

Mensaje:

`No se encontró el archivo: [ruta]`

Acción: verificar `usuarios[].maestro_path` del usuario que se está procesando en `config.json`.

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
- Mantener credenciales actualizadas.

## 10. Soporte

Ante incidentes:

1. Revisar `logs/last_run.log`.
2. Confirmar requisitos instalados.
3. Reportar el error completo al equipo de soporte.
