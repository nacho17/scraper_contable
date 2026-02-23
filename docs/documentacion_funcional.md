# 📙 Documentación Funcional  
## Sistema de Actualización Automática – Grupo2000

---

## 1. Objetivo del Sistema

El sistema tiene como objetivo automatizar el proceso de:

- Descarga de datos desde una plataforma web.
- Procesamiento y transformación de archivos.
- Actualización incremental de un Excel maestro.
- Extensión automática de fórmulas.
- Ejecución manual o programada (scheduler).

Se diseñó para eliminar tareas manuales repetitivas y reducir errores operativos.

---

## 2. Alcance

El sistema:

- Procesa únicamente nuevas fechas no existentes en el Excel maestro.
- No modifica registros históricos ya consolidados.
- No altera estructura de hojas existentes.
- No crea nuevas hojas automáticamente.
- No modifica fórmulas existentes (solo las replica hacia nuevas filas).

---

## 3. Arquitectura General

El sistema está compuesto por:

- Script principal (`main.py`)
- Módulos auxiliares (`utils/`, `excel/`, `web/`)
- Configuración externa (`config.json`)
- Entorno virtual Python (`.venv`)
- Scripts de ejecución para macOS (`setup_mac.sh`, `run.command`)
- Logs de ejecución (`logs/`)

---

## 4. Flujo Funcional

### 4.1 Inicio del Proceso

1. Lectura de configuración desde `config.json`.
2. Validación de credenciales.
3. Validación de existencia del Excel maestro.

---

### 4.2 Extracción de Datos

1. Inicio de sesión en la plataforma web.
2. Descarga del dataset correspondiente.
3. Validación de integridad del archivo descargado.

---

### 4.3 Conversión de Archivos

Si el archivo requiere conversión de formato:

- Se utiliza LibreOffice en modo headless.
- Se detecta automáticamente el ejecutable (`libreoffice` o `soffice`).
- En macOS se contempla la ruta estándar:
  
  /Applications/LibreOffice.app/Contents/MacOS/soffice

---

### 4.4 Procesamiento de Datos

1. Lectura del dataset.
2. Identificación de fechas ya existentes en el Excel maestro.
3. Filtrado de registros nuevos.
4. Preparación de estructura compatible con el Excel destino.

---

### 4.5 Actualización del Excel Maestro

1. Apertura del archivo.
2. Identificación de última fila con datos.
3. Inserción de nuevas filas.
4. Replicación de fórmulas hacia nuevas filas.
5. Guardado del archivo actualizado.

Si no existen nuevas fechas:

- El sistema finaliza sin modificaciones.

---

## 5. Reglas de Negocio

- Solo se insertan registros con fechas no existentes.
- El orden cronológico debe mantenerse.
- No se sobrescriben filas existentes.
- Las fórmulas deben existir en la última fila válida para poder replicarse.
- No se permiten fórmulas tipo array en columnas que deben extenderse.

---

## 6. Configuración

Archivo: `config.json`

Contiene:

- Credenciales de acceso.
- Ruta absoluta del Excel maestro.
- Parámetros necesarios para la conexión.

Separar configuración del código permite:

- Cambiar rutas sin modificar scripts.
- Evitar hardcoding.
- Facilitar despliegues en distintos equipos.

---

## 7. Scheduler (Automatización)

En macOS se utiliza `cron` para ejecución programada.

Ejemplo:

0 8 * * * /bin/bash /Users/usuario/Grupo2000/run.command

Esto permite ejecución diaria automática sin intervención manual.

El sistema es idempotente:  
Si no hay nuevos datos, no produce modificaciones.

---

## 8. Manejo de Errores

El sistema registra eventos en:

logs/last_run.log

Tipos de errores contemplados:

- Fallo de autenticación.
- Dataset inválido o corrupto.
- LibreOffice no disponible.
- Excel maestro inexistente.
- Fórmulas tipo array no compatibles.
- Errores inesperados de ejecución.

Todos los errores quedan registrados para auditoría.

---

## 9. Dependencias

### 9.1 Software Externo

- Python 3
- LibreOffice (modo headless)

### 9.2 Librerías Python

Instaladas desde:

requirements.txt

Gestionadas mediante entorno virtual `.venv`.

---

## 10. Estructura del Proyecto

Estructura simplificada:

Grupo2000/
│
├── main.py
├── config.json
├── requirements.txt
├── setup_mac.sh
├── run.command
├── .venv/
├── logs/
├── excel/
├── utils/
├── web/
└── docs/

---

## 11. Seguridad

- Las credenciales se almacenan en `config.json`.
- No se exponen en el código fuente.
- El repositorio puede mantenerse privado.
- Se recomienda restringir permisos del archivo `config.json`.

---

## 12. Mantenimiento

Recomendaciones:

- Verificar logs periódicamente.
- Mantener Python actualizado.
- Actualizar dependencias cuando sea necesario.
- No modificar manualmente la estructura del Excel maestro sin validar impacto.

---

## 13. Limitaciones Conocidas

- Dependencia de la estabilidad de la plataforma web.
- Dependencia de LibreOffice para conversiones.
- Sensibilidad a cambios estructurales en el Excel maestro.
- No soporta fórmulas array dinámicas en columnas extendibles.

---

## 14. Evolución Futura (Opcional)

Posibles mejoras:

- Migración a `launchd` en macOS.
- Interfaz gráfica mínima.
- Notificaciones por email ante errores.
- Control de versiones del Excel maestro.
- Validaciones adicionales de integridad de datos.

---

## 15. Conclusión

El sistema provee una solución automatizada, controlada y reproducible para la actualización del Excel maestro, reduciendo carga operativa y riesgo de errores manuales.

Su diseño modular permite mantenimiento sencillo y adaptabilidad ante cambios futuros.