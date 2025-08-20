# import requests
# from bs4 import BeautifulSoup

# url = 'moodle.com'
# response = requests.get(url)

# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, 'html.parser')
    
#     student = soup.find_all('a', 'username')

# from bs4 import BeautifulSoup

# # Abrir el archivo HTML
# with open("moodle.html", "r", encoding="utf-8") as f:
#     html_content = f.read()

# # Parsear el HTML con BeautifulSoup
# soup = BeautifulSoup(html_content, "html.parser")

# # Encontrar todas las filas con class="userrow even"
# rows = soup.find_all("tr", class_="userrow even")

# data = []
# for row in rows:
#     # Extraer username
#     username_tag = row.find("a", class_="username")
#     username = username_tag.get_text(strip=True) if username_tag else None

#     # Extraer useridnumber
#     userid_tag = row.find("td", class_="userfield useridnumber cell c2")
#     useridnumber = userid_tag.get_text(strip=True) if userid_tag else None

#     # Extraer useremail
#     email_tag = row.find("td", class_="userfield useremail cell c3")
#     useremail = email_tag.get_text(strip=True) if email_tag else None

#     # Extraer todos los gradevalue
#     grade_tags = row.find_all("span", class_="gradevalue")
#     gradevalues = [g.get_text(strip=True) for g in grade_tags]

#     # Guardar en diccionario
#     data.append({
#         "username": username,
#         "useridnumber": useridnumber,
#         "useremail": useremail,
#         "grades": gradevalues
#     })

# # Mostrar resultados
# for item in data:
#     print(item)


import csv
from bs4 import BeautifulSoup

# Abrir el archivo HTML
with open("moodle.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Parsear el HTML con BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Encontrar todas las filas con class="userrow even"
rows = soup.find_all("tr", class_="userrow even")

data = []
max_grades = 0

for row in rows:
    username_tag = row.find("a", class_="username")
    username = username_tag.get_text(strip=True) if username_tag else None

    userid_tag = row.find("td", class_="userfield useridnumber cell c2")
    useridnumber = userid_tag.get_text(strip=True) if userid_tag else None

    email_tag = row.find("td", class_="userfield useremail cell c3")
    useremail = email_tag.get_text(strip=True) if email_tag else None

    grade_tags = row.find_all("span", class_="gradevalue")
    gradevalues = [g.get_text(strip=True) for g in grade_tags]

    max_grades = max(max_grades, len(gradevalues))

    data.append({
        "username": username,
        "useridnumber": useridnumber,
        "useremail": useremail,
        "grades": gradevalues
    })

# Crear cabecera dinámica
headers = ["username", "useridnumber", "useremail"] + [f"grade{i+1}" for i in range(max_grades)]

# Exportar a CSV
with open("moodle_export.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)

    for item in data:
        row = [item["username"], item["useridnumber"], item["useremail"]] + item["grades"]
        # Rellenar con vacío si le faltan calificaciones
        row += [""] * (max_grades - len(item["grades"]))
        writer.writerow(row)

print("✅ Archivo 'moodle_export.csv' generado con éxito.")
