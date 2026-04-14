# Busqueda_REMATES

Este proyecto es una herramienta para la búsqueda y gestión de remates de inmuebles en Uruguay. Originalmente concebido como un script de scraping (`scraper.py`), ha evolucionado a una aplicación web completa con una interfaz de gestión basada en Flask.

## Características

- **Scraping Multi-fuente**: Extrae datos de IMPO (Diario Oficial), ANRTCI (Rematadores) e Intendencia de Montevideo.
- **Gestión Web**: Visualización de remates en un dashboard intuitivo.
- **Funcionalidades de Usuario**:
    - Marcar remates como "vistos".
    - Agregar notas personalizadas a cada remate.
    - Eliminar remates que no sean de interés.
    - Exportar la lista filtrada a CSV.
- **Base de Datos Local**: Almacenamiento persistente en SQLite (`remates.db`).

## Configuración para Puppy Linux

Si estás ejecutando este proyecto en un entorno Puppy Linux, consulta [PUPPYLINUX.md](file:///root/PERSONAL_ORGANIZER/REMATES/PUPPYLINUX.md) para conocer los ajustes necesarios de permisos y dependencias.

## Instalación

1. **Clonar el repositorio**:
    ```bash
    git clone https://github.com/ukoquique-proves/remates-uy
    cd remates-uy
    ```

2. **Instalar dependencias**:
    ```bash
    pip install requests beautifulsoup4 Flask
    ```

## Uso

### Aplicación Web (Recomendado)

Inicia el servidor Flask para acceder al dashboard:
```bash
python3 app.py
```
Luego, abre tu navegador en `http://localhost:5000`. Desde el dashboard puedes iniciar nuevos scrapings presionando el botón correspondiente.

### Solo Scraper (CLI)

Si prefieres ejecutar solo el proceso de extracción sin la interfaz web:
```bash
python3 scraper.py
```

## Fuentes de Datos

- **IMPO (Diario Oficial)**: Foco en Montevideo, filtrando inmuebles/terrenos.
- **ANRTCI**: Asociación Nacional de Rematadores.
- **Intendencia de Montevideo**: Cartelera de remates judiciales (puede estar desactualizada).

## Contribución

El proyecto sigue una arquitectura minimalista. Para añadir fuentes, modifica `scraper.py` añadiendo nuevas funciones `scrape_`. La base de datos y la interfaz se actualizan automáticamente al integrar nuevas fuentes en el flujo principal.
