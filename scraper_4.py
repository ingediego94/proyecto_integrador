import requests
from bs4 import BeautifulSoup
import csv
import re

BASE_URL = "https://riwi-test.unhosting.site"
LOGIN_URL = f"{BASE_URL}/login/index.php"
REPORT_URL = f"{BASE_URL}/report/log/index.php"

USERNAME = "riwipruebas"
PASSWORD = "Riwi2025*"

PARAMS = {
    "chooselog": "1",
    "showusers": "0",
    "showcourses": "0",
    "id": "60",
    "user": "0",
    "date": "",
    "modid": "",
    "modaction": "",
    "origin": "web",
    "edulevel": "1",
    "logreader": "logstore_standard"
}

# Eventos permitidos (columna c5)
ALLOWED_EVENTS = {
    "Usuario calificado",
    "Intento enviado",
    "Intento del cuestionario revisado",
    "Intento de cuestionario actualizado",
    "Anulación de tarea creada",
    "Formulario de calificaciones visto",
    "Visualización de las calificaciones",
    "Se ha calificado el envío"
}

def extract_id_from_href(href):
    """Extrae el número después de id= y antes de & en un link."""
    match = re.search(r"id=(\d+)", href)
    return match.group(1) if match else None

def get_last_page(soup):
    """Encuentra la última página en la paginación."""
    pagination = soup.find_all("li", class_="page-item")
    if not pagination:
        return 1
    pages = [int(li["data-page-number"]) for li in pagination if li.has_attr("data-page-number")]
    return max(pages) if pages else 1

# Crear sesión
session = requests.Session()

# 1. Obtener logintoken
resp = session.get(LOGIN_URL)
soup = BeautifulSoup(resp.text, "html.parser")
token_input = soup.find("input", {"name": "logintoken"})
logintoken = token_input["value"] if token_input else ""

# 2. Hacer login
payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "logintoken": logintoken
}
login_response = session.post(LOGIN_URL, data=payload)

if "logout" not in login_response.text.lower():
    print("Error: No se pudo iniciar sesión en Moodle.")
    exit()

print("Login exitoso.")

# 3. Scraping del reporte
all_rows = []
headers = []

page = 0
while True:
    params = PARAMS.copy()
    if page > 0:
        params["page"] = str(page)

    response = session.get(REPORT_URL, params=params)
    if response.status_code != 200:
        break

    soup = BeautifulSoup(response.text, "html.parser")

    # Capturar encabezados una sola vez (solo c0 a c6)
    if not headers:
        headers = [th.get_text(strip=True) for th in soup.select("th.header") if th["class"][-1] in [f"c{i}" for i in range(0, 7)]]

    # Capturar filas
    rows = soup.find_all("tr", id=re.compile(r"report_log_r\d+"))
    if not rows:
        break

    for row in rows:
        row_data = []

        # c0 (Hora) → limpiar coma y comillas
        cell0 = row.find("td", class_="cell c0")
        fecha_hora = cell0.get_text(strip=True) if cell0 else ""
        fecha_hora = fecha_hora.replace(",", "").replace('"', "")
        row_data.append(fecha_hora)

        # c1 con link
        cell1 = row.find("td", class_="cell c1")
        link1 = cell1.find("a")["href"] if cell1 and cell1.find("a") else ""
        row_data.append(extract_id_from_href(link1) if link1 else "")

        # c2 con link
        cell2 = row.find("td", class_="cell c2")
        link2 = cell2.find("a")["href"] if cell2 and cell2.find("a") else ""
        row_data.append(extract_id_from_href(link2) if link2 else "")

        # c3 - c6 (modificando c3 para extraer ID desde href)
        for i in range(3, 7):
            cell = row.find("td", class_=f"cell c{i}")
            if i == 3:
                link = cell.find("a")["href"] if cell and cell.find("a") else ""
                id_from_href = extract_id_from_href(link) if link else ""
                row_data.append(id_from_href)
            else:
                row_data.append(cell.get_text(strip=True) if cell else "")

        # Filtrar por evento (columna c5)
        event_name = row_data[5] if len(row_data) > 5 else ""
        if event_name in ALLOWED_EVENTS:
            all_rows.append(row_data)

    # Verificar última página
    last_page = get_last_page(soup)
    page += 1
    if page >= last_page:
        break

# 4. Guardar en CSV (UTF-8 con BOM)
with open("riwi_logs_4x.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(all_rows)

print("Archivo 'riwi_logs.csv' generado con éxito (UTF-8 con BOM).")
