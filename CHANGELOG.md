# CHANGELOG

## 2026-04-12

### `scraper.py`

-   **Implementación inicial**: Se creó el script `scraper.py` con funciones para extraer avisos de remates de tres fuentes: IMPO, ANRTCI e Intendencia de Montevideo.
    -   Se utilizó `requests` para la obtención de contenido HTML y `BeautifulSoup` para el parseo.
    -   Se incluyeron cabeceras `User-Agent` y un `TIMEOUT` para las peticiones.
    -   Se añadió manejo básico de errores con `try-except` y `traceback`.
    -   Se implementó un resumen final de los resultados de todas las fuentes.

-   **Mejora en `scrape_impo` (v1)**: Se refactorizó la función `scrape_impo` para mejorar la extracción de remates de la fuente IMPO.
    -   Se cambió la lógica de búsqueda de la sección "MONTEVIDEO" para encontrarla como un nodo de texto.
    -   Se ajustó la recolección de texto para iterar a través de `next_element` y detectar el inicio de la siguiente sección de departamento.
    -   Se añadió un filtro por palabras clave (`keywords_inmueble`) para identificar solo inmuebles/terrenos.
    -   Se implementó la extracción de enlaces a los avisos individuales.

-   **Corrección de `NameError: name 're' is not defined`**: Se identificó y corrigió un error donde la importación del módulo `re` se había perdido, causando un `NameError`. Se aseguró que `import re` estuviera presente al inicio del archivo.

-   **Mejora en `scrape_impo` (v2)**: Se ajustó la lógica de `scrape_impo` para buscar la sección "MONTEVIDEO" dentro de una etiqueta `<p>` (ya que el HTML de IMPO la presenta así) y luego iterar a través de los `next_siblings` de esa etiqueta `<p>` para recolectar el contenido de la sección.

-   **Mejora en `scrape_impo` (v3)**: Se refinó la lógica de `scrape_impo` para que la búsqueda de la sección "MONTEVIDEO" sea más flexible, buscando si el texto de la etiqueta `<p>` *contiene* la palabra "MONTEVIDEO" (ignorando mayúsculas/minúsculas y espacios extra). Se ajustó la detección del siguiente departamento para ser más robusta.

-   **Mejora en `scrape_impo` (v4)**: Se corrigió la lógica de `scrape_impo` para iterar correctamente a través de los `next_siblings` de la etiqueta `<p>` que contiene "MONTEVIDEO", asegurando que se recolecte todo el contenido de la sección hasta el siguiente departamento. Esta versión final logró extraer con éxito los remates de IMPO.

### `app.py` & Web UI

- **Implementación del Dashboard**: Se creó una aplicación Flask para gestionar los remates de forma visual.
- **Interactividad**: Añadida capacidad para marcar remates como vistos, añadir notas y eliminar registros.
- **Persistencia**: Integración con SQLite (`remates.db`) para mantener el estado de las notas y el estado de visualización entre scrapings.
- **Exportación**: Añadida funcionalidad para exportar la base de datos a CSV desde la interfaz web.
- **Trigger de Scraping**: Integración directa del script `scraper.py` ejecutable desde el navegador.
