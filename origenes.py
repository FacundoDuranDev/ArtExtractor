import requests
from bs4 import BeautifulSoup
import os
import time

# Rango de IDs de prueba
start_id = 0
end_id = 2000
delay = 1  # Pausa entre solicitudes para evitar sobrecargar el servidor

# Crear un directorio para guardar las imágenes
os.makedirs('imagenes_obras', exist_ok=True)

# Base URL de las obras
base_url = "https://www.bellasartes.gob.ar/coleccion/obra/"
base_url_img = "https://www.bellasartes.gob.ar/"

for obra_id in range(start_id, end_id + 1):
    url = f"{base_url}{obra_id}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Obra encontrada en {url}")
        
        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer el título de la obra
        titulo_tag = soup.find('h1')
        titulo = titulo_tag.text.strip() if titulo_tag else "Título no encontrado"
        details_div = soup.find('dl', class_='row mt-3')
        img_tag = soup.find('a', {'data-fancybox': 'gallery'})
        if details_div:
            li_elements = details_div.find_all('li')
            lista_texto = []
            for li in li_elements:
                lista_texto.append(li.text.strip())  # Mostrar el texto del elemento <li>
        
        
        if img_tag and 'href' in img_tag.attrs:
            img_url = img_tag['href']
            print(f"URL de la imagen: {img_url}")

            img_response = requests.get(base_url_img + img_url)
            if img_response.status_code == 200:
                # Crear la ruta del directorio si no existe
                dir_path = os.path.join('imagenes_obras', lista_texto[0].replace(",", ""))
                os.makedirs(dir_path, exist_ok=True)  # Crear directorio si no existe
                
                # Guardar la imagen
                img_filename = os.path.join(dir_path, f"{titulo}.jpg")
                with open(img_filename, 'wb') as f:
                    f.write(img_response.content)
    print(f"obra no encontrada {url}")