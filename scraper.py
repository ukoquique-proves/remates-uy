import re
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import traceback
import sqlite3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15

def save_to_db(data, db_path="remates.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fuente TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                link TEXT,
                notas TEXT,
                visto INTEGER DEFAULT 0,
                fecha_scrape TEXT DEFAULT (date('now'))
            )
        """)
        conn.commit()

        # Insert data
        for item in data:
            cursor.execute("""
                INSERT INTO remates (fuente, descripcion, link)
                VALUES (?, ?, ?)
            """, (item["fuente"], item["descripcion"], item["link"]))
        conn.commit()
        print(f"\nResultados guardados exitosamente en {db_path}")

    except sqlite3.Error as e:
        print(f"\nError al guardar en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

# ─────────────────────────────────────────
# FUENTE 1: IMPO — HTML estático, datos frescos
# Estructura confirmada: bloques de texto plano separados por sección de departamento
# ─────────────────────────────────────────
def _find_montevideo_section(soup):
    for tag in soup.find_all("p"):
        if "MONTEVIDEO" in tag.get_text(strip=True).upper():
            return tag
    return None

def _collect_section_text(start_tag):
    textos = []
    for sibling in start_tag.next_siblings:
        # Heurística para detectar el inicio del siguiente departamento:
        # un tag <p> cuyo texto es todo en mayúsculas y tiene entre 5 y 29 caracteres.
        # Estos "números mágicos" (4 y 30) se basan en la observación del HTML actual
        # de IMPO y podrían necesitar ajuste si el formato cambia.
        if sibling.name == "p" and sibling.get_text(strip=True).isupper() and 4 < len(sibling.get_text(strip=True)) < 30 and "MONTEVIDEO" not in sibling.get_text(strip=True).upper():
            break
        if hasattr(sibling, "get_text"):
            textos.append(sibling.get_text(separator=" ", strip=True))
        elif isinstance(sibling, str):
            textos.append(sibling.strip())
    return " ".join(t for t in textos if t)

def _split_into_auction_blocks(text):
    bloques = re.split(r'(?=Fecha:\s*\d{2}/\d{2}/\d{4})', text)
    return [b.strip() for b in bloques if b.strip() and "Fecha:" in b]

def _filter_inmuebles(blocks):
    keywords_inmueble = [
        "terreno", "solar", "fracción", "fraccion",
        "inmueble", "padrón", "padron", "superficie",
        "propiedad horizontal", "bien inmueble"
    ]
    return [
        b for b in blocks
        if any(kw in b.lower() for kw in keywords_inmueble)
    ]

def scrape_impo():
    url = "http://www.impo.com.uy/remates"
    print("\n" + "="*50)
    print(f"FUENTE 1: IMPO — {url}")
    print("="*50)

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        print(f"Status HTTP: {response.status_code}")
        response.encoding = "iso-8859-1"

        soup = BeautifulSoup(response.text, "html.parser")

        seccion_mvd_tag = _find_montevideo_section(soup)
        if not seccion_mvd_tag:
            print("⚠️  No se encontró la sección MONTEVIDEO como tag <p>.")
            print("    Posibles nombres de departamento encontrados en tags <p>:")
            for tag in soup.find_all("p"):
                t = tag.get_text(strip=True)
                if t.isupper() and 4 < len(t) < 30:
                    print(f"      '{t}'")
            return [], "Sección MONTEVIDEO no encontrada como tag <p>"

        texto_mvd = _collect_section_text(seccion_mvd_tag)
        print(f"\nTexto MONTEVIDEO capturado ({len(texto_mvd)} chars):")
        print(texto_mvd[:400])
        print("...\n")

        bloques = _split_into_auction_blocks(texto_mvd)
        print(f"Bloques de remate en MONTEVIDEO: {len(bloques)}")

        inmuebles = _filter_inmuebles(bloques)
        print(f"De esos, inmuebles/terrenos: {len(inmuebles)}\n")

        # Debido a la inconsistencia en los identificadores entre el texto del bloque
        # y los enlaces, no es posible asociar de forma fiable cada bloque con un
        # enlace específico de "avisos-remate". Por lo tanto, se usará la URL base
        # de IMPO para todos los resultados de esta fuente.
        resultados = []
        for bloque in inmuebles:
            resultados.append({
                "fuente": "IMPO (Diario Oficial)",
                "descripcion": bloque[:400],
                "link": url  # Usar la URL base de IMPO
            })
            print(f"  ✅ {bloque[:250]}")
            print(f"  🔗 {url}\n")

        return resultados, None

    except RequestException as e:
        err = f"Error de conexión: {e}"
        print(f"ERROR:\n{err}")
        return [], err
    except Exception:
        err = traceback.format_exc()
        print(f"ERROR:\n{err}")
        return [], err


# ─────────────────────────────────────────
# FUENTE 2: ANRTCI — intentamos las dos URLs conocidas
# ─────────────────────────────────────────
def scrape_anrtci():
    urls_a_probar = [
        "https://anrtci.uy/web/remates.php",
        "https://www.anrtci.uy/web/remates.php",
        "https://anrtci.uy/remates.php",
    ]
    print("\n" + "="*50)
    print("FUENTE 2: ANRTCI")
    print("="*50)

    html = None
    url_ok = None
    for url in urls_a_probar:
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            print(f"  {url} → Status: {response.status_code}")
            if response.status_code == 200 and len(response.text) > 500:
                html = response.text
                url_ok = url
                break
        except RequestException as e:
            print(f"  {url} → Error de conexión: {e}")
        except Exception as e:
            print(f"  {url} → Error inesperado: {e}")

    if not html:
        msg = "Ninguna URL de ANRTCI respondió con contenido válido"
        print(f"\n⚠️  {msg}")
        return [], msg

    print(f"\nUsando: {url_ok}")
    print("\n--- HTML crudo (primeros 1500 chars) ---")
    print(html[:1500])
    print("--- fin muestra ---\n")

    soup = BeautifulSoup(html, "html.parser")

    # Basado en búsqueda anterior: cards con dirección, padrón, "Más Información"
    # Intentamos varios selectores posibles
    candidatos = (
        soup.select(".remate-item") or
        soup.select(".card") or
        soup.select("article") or
        soup.select(".item-remate") or
        soup.find_all("div", class_=lambda c: c and "remate" in c.lower())
    )

    print(f"Elementos encontrados: {len(candidatos)}")

    resultados = []
    for el in candidatos:
        texto = el.get_text(separator=" ", strip=True)
        if len(texto) < 20:
            continue

        link_tag = el.find("a", href=True)
        link = link_tag["href"] if link_tag else url_ok
        if link and not link.startswith("http"):
            link = "https://anrtci.uy/" + link.lstrip("/")

        resultados.append({
            "fuente": "ANRTCI (Rematadores)",
            "descripcion": texto[:300],
            "link": link
        })
        print(f"  ✅ {texto[:200]}\n  🔗 {link}\n")

    if not resultados:
        msg = "Se obtuvo HTML pero no se encontraron elementos con los selectores conocidos."
        print(f"⚠️  {msg}")
        print("    Revisá el HTML crudo de arriba para identificar la estructura real.")
        return [], msg

    return resultados, None


# ─────────────────────────────────────────
# FUENTE 3: Intendencia de Montevideo
# ADVERTENCIA: última actualización 23/12/2025, datos de 2021 → fuente desactualizada
# Se incluye para completitud pero los datos pueden ser obsoletos
# ─────────────────────────────────────────
def scrape_intendencia():
    url = "https://tramites.montevideo.gub.uy/tramites-y-tributos/registro/cartelera-de-remates-judiciales"
    print("\n" + "="*50)
    print(f"FUENTE 3: Intendencia de Montevideo — {url}")
    print("⚠️  ADVERTENCIA: Esta página tiene última actualización 23/12/2025")
    print("    Los remates listados pueden estar desactualizados")
    print("="*50)

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        print(f"Status HTTP: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        contenido = soup.find(id="main-content") or soup.find("main") or soup.body
        parrafos = []
        if contenido:
            parrafos = contenido.find_all(["p", "li"])

        resultados = []
        for p in parrafos:
            texto = p.get_text(strip=True)
            if "padrón" in texto.lower() or "padron" in texto.lower():
                # Excluir los ya rematados
                if "REMATADO" not in texto:
                    resultados.append({
                        "fuente": "Intendencia de Montevideo",
                        "descripcion": texto[:300],
                        "link": url
                    })
                    print(f"  ✅ {texto[:200]}\n")

        if not resultados:
            msg = "Sin remates vigentes (todos marcados REMATADO o página desactualizada)"
            print(f"  {msg}")
            return [], msg

        return resultados, None


    except RequestException as e:
        err = f"Error de conexión: {e}"
        print(f"ERROR:\n{err}")
        return [], err
    except Exception:
        err = traceback.format_exc()
        print(f"ERROR:\n{err}")
        return [], err


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    all_auction_results = []
    errores = {}

    r1, e1 = scrape_impo()
    all_auction_results.extend(r1)
    if e1:
        errores["IMPO"] = e1

    r2, e2 = scrape_anrtci()
    all_auction_results.extend(r2)
    if e2:
        errores["ANRTCI"] = e2

    r3, e3 = scrape_intendencia()
    all_auction_results.extend(r3)
    if e3:
        errores["Intendencia"] = e3

    # ── RESUMEN FINAL ──
    print("\n" + "="*50)
    print("RESUMEN")
    print("="*50)
    print(f"IMPO:         {len(r1)} inmuebles/terrenos en Montevideo")
    print(f"ANRTCI:       {len(r2)} remates encontrados")
    print(f"Intendencia:  {len(r3)} remates vigentes")
    print(f"TOTAL:        {len(all_auction_results)} resultados")

    if errores:
        print("\nERRORES:")
        for fuente, err in errores.items():
            print(f"  {fuente}: {err[:200]}")
    else:
        print("\nSin errores de conexión.")

    save_to_db(all_auction_results, "remates.db")