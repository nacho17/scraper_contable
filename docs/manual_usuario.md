# 📘 Manual de Usuario  
## Sistema de Actualización Automática – Grupo2000

---

## 1. Descripción General

El sistema permite:

- Descargar automáticamente el dataset desde la plataforma web.
- Procesar la información.
- Insertar los nuevos registros en el Excel maestro.
- Mantener actualizadas las fórmulas.
- Generar logs de ejecución.

El objetivo es que el Excel maestro se mantenga actualizado sin intervención manual.

---

## 2. Requisitos

Antes de utilizar el sistema, asegúrese de tener:

- Python 3 instalado.
- LibreOffice instalado.
- Acceso a internet.
- Archivo Excel maestro existente.

---

## 3. Instalación en macOS

### Paso 1 – Clonar el repositorio

Clonar el proyecto en una carpeta del equipo.

Ejemplo:

/Users/usuario/Grupo2000

---

### Paso 2 – Configurar credenciales

Editar el archivo:

config.json

Completar:

- Usuario
- Contraseña
- Ruta completa del Excel maestro

Guardar los cambios.

---

### Paso 3 – Ejecutar el script de instalación

Desde la carpeta del proyecto ejecutar:

bash setup_mac.sh

Este proceso:

- Verifica Python
- Verifica LibreOffice
- Crea el entorno virtual
- Instala dependencias
- Crea un acceso directo en el Escritorio

---

### Paso 4 – Ejecutar el sistema

En el Escritorio se crea el archivo:

Grupo2000.command

Para ejecutar el sistema:

- Hacer doble clic sobre ese archivo.

---

## 4. Programación automática (Scheduler)

Si se desea ejecución automática diaria:

1. Abrir Terminal.
2. Ejecutar:

crontab -e

3. Agregar una línea similar a:

0 8 * * * /bin/bash /Users/usuario/Grupo2000/run.command

Esto ejecutará el sistema todos los días a las 08:00.

Guardar y cerrar.

Para verificar:

crontab -l

---

## 5. Funcionamiento general

Cuando el sistema se ejecuta:

1. Inicia sesión en la plataforma web.
2. Descarga el dataset.
3. Convierte archivos si es necesario (requiere LibreOffice).
4. Inserta nuevos registros en el Excel maestro.
5. Estira las fórmulas.
6. Guarda el archivo actualizado.

Si no hay nuevas fechas para procesar, el sistema finaliza sin modificar el Excel.

---

## 6. Logs y seguimiento

Los logs se almacenan en:

logs/last_run.log

Allí se puede verificar:

- Errores
- Procesos ejecutados
- Mensajes informativos

---

## 7. Manejo de Errores

### Error de autenticación

Mensaje:

ERROR: Problema de autenticación. Revise usuario/contraseña en config.json.

Solución:

1. Abrir config.json.
2. Verificar usuario y contraseña.
3. Guardar.
4. Ejecutar nuevamente.

---

### LibreOffice no instalado

Mensaje en log:

LibreOffice no está instalado o no está en el PATH.

Solución:

- Instalar LibreOffice.
- Volver a ejecutar el sistema.

---

### Excel maestro no encontrado

Mensaje:

No se encontró el archivo: [ruta]

Solución:

- Verificar que el archivo exista.
- Confirmar que la ruta en config.json sea correcta.

---

### Error con fórmulas tipo Array

Si el Excel maestro contiene fórmulas tipo array (entre llaves `{}`) en las columnas donde el sistema debe estirar fórmulas, la ejecución fallará.

Mensaje:

No se pueden estirar formulas tipo array en el Excel maestro.

Solución:

1. Abrir el Excel maestro.
2. Verificar la última fila de la hoja destino.
3. Eliminar fórmulas tipo array en las columnas afectadas.
4. Guardar el archivo.
5. Ejecutar nuevamente.

Importante:  
Este problema depende del estado del Excel. Una vez corregido, no debería repetirse.

---

## 8. Recomendaciones

- No modificar manualmente las últimas filas del Excel mientras el sistema esté en uso.
- No utilizar fórmulas array en columnas donde se insertan datos automáticamente.
- Verificar periódicamente el archivo de log.
- Mantener actualizadas las credenciales si cambian.

---

## 9. Soporte

Ante cualquier inconveniente:

- Revisar primero el archivo de log.
- Confirmar que los requisitos estén instalados.
- Contactar al proveedor del sistema indicando el mensaje de error completo.