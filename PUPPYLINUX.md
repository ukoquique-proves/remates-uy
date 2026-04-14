# Adaptación a Puppy Linux (Entorno de Remates)

Este documento explica los ajustes necesarios para que el proyecto de Remates funcione correctamente en este entorno basado en Puppy Linux.

## 1. Permisos del Sistema de Archivos
Puppy Linux a menudo utiliza sistemas de archivos en capas (overlayfs) que pueden restringir la escritura en directorios raíz. Para este proyecto, se requirió acceso total a `/root/PERSONAL_ORGANIZER/REMATES`.

**Solución aplicada:**
Se ejecutó el siguiente comando desde la consola para habilitar permisos de escritura en todo el árbol de directorios:
```bash
chmod -R 777 /root/PERSONAL_ORGANIZER
```

## 2. Gestión de Dependencias Python
Debido a que el entorno utiliza una instalación de Python gestionada externamente (PEP 668), no se recomienda el uso de `pip install` a nivel de sistema.

**Configuración actual:**
Las dependencias se instalaron directamente en la carpeta del proyecto para evitar conflictos y asegurar que el servidor Flask tenga acceso a ellas:
```bash
pip install -t . flask requests beautifulsoup4 --break-system-packages
```

## 3. Base de Datos SQLite
La base de datos `remates.db` se encuentra ahora en el directorio raíz del proyecto. Gracias al ajuste de permisos del punto 1, tanto el servidor web como el script de scraping pueden leer y escribir sin problemas.

## 4. Ejecución del Proyecto
Para iniciar la aplicación, simplemente ejecuta el script principal desde la terminal:
```bash
python3 app.py
```
La aplicación estará disponible en `http://127.0.0.1:5000`.

## 5. Notas sobre el Scraping
El botón **"Scrapear Ahora"** en la interfaz web ejecuta el script `scraper.py` como un subproceso. Asegúrate de que los permisos de ejecución se mantengan si mueves el proyecto a otra ubicación.
