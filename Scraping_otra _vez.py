from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

# URL base
BASE_URL = "https://archivopatrimonial.uahurtado.cl/"
START_URL = "https://archivopatrimonial.uahurtado.cl/index.php/taxonomy/index/id/35?page=1&limit=20&sort=alphabetic&sortDir=asc"

import subprocess

def setup_driver():
    print("---------------------------------------------------------")
    print("INTENTO AUTOMÁTICO: REINICIANDO CHROME")
    print("---------------------------------------------------------")
    
    # 1. Matar procesos antiguos de Chrome
    try:
        print("Cerrando instancias viejas de Chrome...")
        subprocess.run("taskkill /f /im chrome.exe", shell=True, stderr=subprocess.DEVNULL)
        time.sleep(2)
    except Exception:
        pass

    # 2. Lanzar Chrome con el puerto abierto
    print("Lanzando Chrome en modo debug...")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\Users\nakoo\AppData\Local\Google\Chrome\User Data"
    
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--profile-directory=Default",
        "--no-first-run",
        "--no-default-browser-check",
        "https://archivopatrimonial.uahurtado.cl"
    ]
    
    # Lanzar proceso en segundo plano
    chrome_process = subprocess.Popen(cmd)
    print("Chrome lanzado. Esperando 5 segundos...")
    time.sleep(5)

    print("Conectando Selenium...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"\nERROR CRÍTICO: No se pudo conectar.")
        print(f"Detalle: {e}")
        # Si falla, no matamos el proceso para que el usuario pueda ver qué pasó
        raise e

def extract_documents_from_category(driver, category_url):
    print(f"Navegando a categoría: {category_url}")
    try:
        driver.get(category_url)
        time.sleep(2) # Esperar a que cargue JS si lo hay
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        documents = []
        
        # Buscamos enlaces de documentos
        # Ajustamos el selector según lo que se vea en el HTML real
        document_links = soup.select('div.content a') 
        if not document_links:
            document_links = soup.select('a')

        for link in document_links:
            title = link.text.strip()
            href = link.get('href')
            
            if href and title:
                full_href = urljoin(BASE_URL, href)
                
                # Filtros básicos para no guardar basura
                if "index.php" in full_href and title != "Log in" and len(title) > 3:
                     if not any(d['href'] == full_href for d in documents):
                        documents.append({"title": title, "href": full_href})
        
        return documents
    except Exception as e:
        print(f"Error en categoría {category_url}: {e}")
        return []

def scrape_categories(driver, start_url):
    print(f"Abriendo página principal: {start_url}")
    try:
        driver.get(start_url)
        time.sleep(3) # Esperar carga inicial
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        categories = []
        
        # Intentamos selectores para la tabla de taxonomía
        category_links = soup.select('table tbody tr td a')
        if not category_links:
             # Selector alternativo si la estructura es diferente
             category_links = soup.select('.taxonomy-browse a, .term a')

        print(f"Encontrados {len(category_links)} posibles enlaces de categoría.")

        for category_link in category_links:
            category_name = category_link.text.strip()
            raw_url = category_link.get('href')
            
            if raw_url:
                category_url = urljoin(BASE_URL, raw_url)
                
                # Evitar recusividad o enlaces rotos
                if "taxonomy" in category_url or "informationobject" in category_url: 
                    cat_docs = extract_documents_from_category(driver, category_url)
                    
                    if cat_docs:
                        categories.append({
                            "category": category_name,
                            "documents": cat_docs
                        })
    
        return categories
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []

def save_to_json(data, filename="archivos_patrimoniales_por_categoria.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {filename}")

def main():
    driver = None
    try:
        driver = setup_driver()
        categories = scrape_categories(driver, START_URL)
        save_to_json(categories)
        print(f"Total de categorías extraídas: {len(categories)}")
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        if driver:
            print("Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    main()
