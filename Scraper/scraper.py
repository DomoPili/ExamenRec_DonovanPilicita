"""
Archivo: scraper.py
Descripción: Lógica completa para extraer SEGUIDOS (Following) y detalles de perfiles.
"""

import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import INSTAGRAM_URLS, SCRAPING_CONFIG
from utils import human_delay, extract_username_from_url, parse_follower_count
import html


# =====================================================================
# FUNCIONES AUXILIARES (EXTRACCIÓN DE DATOS)
# =====================================================================

def _extract_from_meta_description(content):
    """Extrae información de la meta description"""
    if not content:
        return None, None
    parts = content.split(' - ', 1)
    if len(parts) == 2:
        left, right = parts
        right = right.split('See Instagram', 1)[0].split('See posts', 1)[0].strip()
        return left.strip(), right.strip()
    return content.strip(), None

def _get_followers_from_spans(driver):
    """Intenta obtener followers desde spans"""
    try:
        spans_with_title = driver.find_elements(By.XPATH, "//span[@title]")
        for span in spans_with_title:
            title = span.get_attribute('title')
            if title and title.replace(',', '').replace('.', '').isdigit():
                return parse_follower_count(title)
    except Exception:
        pass
    return None

def _get_followers_from_meta(driver):
    """Intenta obtener followers desde meta tags"""
    try:
        meta_element = driver.find_element(By.XPATH, "//meta[@property='og:description']")
        content = meta_element.get_attribute('content')
        left_text, _ = _extract_from_meta_description(content)
        m = re.search(r'([\d,\.KMB]+)\s+[Ff]ollowers?', left_text)
        if m:
            return parse_follower_count(m.group(1))
    except Exception:
        pass
    return None

def _get_followers_from_page_source(driver):
    """Intenta obtener followers desde el código fuente"""
    try:
        page_source = driver.page_source
        patterns = [r'"edge_followed_by":\{"count":(\d+)\}', r'"follower_count":(\d+)']
        for pattern in patterns:
            match = re.search(pattern, page_source)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return None

def _get_following_from_spans(driver):
    """Intenta obtener el número de SEGUIDOS desde los elementos <span>"""
    try:
        all_text = driver.find_element(By.TAG_NAME, "header").text.lower()
        match = re.search(r'(\d+(?:[.,]\d+)*)\s+seguidos\b', all_text)
        if match:
            return int(match.group(1).replace(',', '').replace('.', ''))
        match = re.search(r'(\d+(?:[.,]\d+)*)\s+following\b', all_text)
        if match:
            return int(match.group(1).replace(',', '').replace('.', ''))
    except Exception:
        pass
    return None

def _get_following_from_meta(driver):
    """Intenta obtener el número de seguidos desde las meta tags"""
    try:
        meta_element = driver.find_element(By.XPATH, "//meta[@property='og:description']")
        content = meta_element.get_attribute('content')
        m = re.search(r'([\d,\.KMB]+)\s+[Ff]ollowing', content)
        if m:
            return parse_follower_count(m.group(1))
    except Exception:
        pass
    return None

def _get_following_from_page_source(driver):
    """Intenta obtener el número de seguidos desde el código fuente"""
    try:
        page_source = driver.page_source
        patterns = [
            r'"edge_follow":\s*\{\s*"count":\s*(\d+)',
            r'"following_count":\s*(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, page_source)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return None

def _get_full_name(driver):
    """Intenta obtener el nombre completo (Name)"""
    try:
        meta = driver.find_element(By.XPATH, "//meta[@property='og:title']")
        content = meta.get_attribute('content')
        match = re.match(r'^(.+?)\s*\(@', content)
        if match:
            name = match.group(1).strip()
            if name and not name.startswith('@'):
                return name
    except Exception:
        pass
    
    try:
        header_sections = driver.find_elements(By.XPATH, "//header//section//h1 | //header//section//h2")
        for h in header_sections:
            text = h.text.strip()
            if text and '@' not in text:
                return text
    except:
        pass
    return None

def get_bio(driver):
    """
    [MODIFICADO] Intenta obtener la biografía del perfil de forma robusta.
    Evita capturar el conteo de "seguidos"
    """
    try:
        # data-testid es la forma más directa y estable
        bio_element = driver.find_element(By.XPATH, "//div[@data-testid='user-bio']")
        bio_text = bio_element.text.strip()
        if bio_text:
            # Limpiar si capturó "X seguidos" por error
            bio_text = re.sub(r'\d+\s+seguidos?', '', bio_text).strip()
            bio_text = re.sub(r'\d+\s+following', '', bio_text, flags=re.IGNORECASE).strip()
            if bio_text:
                return bio_text
    except Exception:
        pass

    # fallback: buscar en header divs (texto que no contenga "followers" o "publicaciones")
    try:
        header_divs = driver.find_elements(By.XPATH, "//header//div")
        candidate_texts = []
        for div in header_divs:
            try:
                txt = div.text.strip()
                if txt and len(txt) > 5:
                    candidate_texts.append(txt)
            except Exception:
                continue
        
        for t in sorted(candidate_texts, key=lambda x: len(x), reverse=True):
            low = t.lower()
            # Filtrar textos que no son bio
            if any(word in low for word in ['followers', 'seguidores', 'following', 'posts', 
                                             'publicaciones', 'seguidos', 'siguiendo']):
                continue
            # Limpiar y retornar
            clean_bio = t.split('\n')[0].strip()
            if clean_bio and len(clean_bio) > 3:
                return clean_bio
    except Exception:
        pass

    # último recurso: meta og:description
    try:
        meta_element = driver.find_element(By.XPATH, "//meta[@property='og:description']")
        content = meta_element.get_attribute('content')
        _, possible_bio = _extract_from_meta_description(content)
        if possible_bio:
            # Limpiar patrones de seguidos
            possible_bio = re.sub(r'\d+\s+seguidos?', '', possible_bio).strip()
            possible_bio = re.sub(r'\d+\s+following', '', possible_bio, flags=re.IGNORECASE).strip()
            if possible_bio and len(possible_bio) > 3:
                return possible_bio
    except Exception:
        pass

    return None



# =====================================================================
# FUNCIONES PRINCIPALES DE SCRAPING
# =====================================================================

def scrape_following(driver, profile, limit):
    """
    Scrapea la lista de SEGUIDOS (Following) de un perfil.
    """
    print(f"\n🔍 Accediendo al perfil de @{profile} para ver a quién sigue...")
    driver.get(INSTAGRAM_URLS['profile'].format(username=profile))
    human_delay(3, 5)

    wait = WebDriverWait(driver, SCRAPING_CONFIG['default_timeout'])
    following_users = set()

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
        print("✅ Perfil cargado correctamente")
    except TimeoutException:
        print("❌ No se pudo cargar el perfil.")
        return set()

    try:
        following_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following')]"))
        )
        driver.execute_script("arguments[0].click();", following_link)
        time.sleep(3)
        print("✅ Modal de 'Seguidos' abierto")
    except Exception:
        print("❌ No se pudo abrir el modal de following")
        return set()

    modal = None
    try:
        posibles = driver.find_elements(By.XPATH, "//div[@role='dialog']//div[@class]")
        for div in posibles:
            try:
                scroll_height = driver.execute_script("return arguments[0].scrollHeight", div)
                client_height = driver.execute_script("return arguments[0].clientHeight", div)
                if scroll_height > client_height + 50:
                    modal = div
                    break
            except:
                continue
    except Exception:
        pass

    if not modal:
        try:
            modal = driver.find_element(By.XPATH, "//div[@role='dialog']//div[contains(@style, 'height: 100%')]")
        except:
            print("❌ No se encontró el contenedor desplazable del modal.")
            return set()

    last_scroll_position = 0
    no_change_count = 0

    while len(following_users) < limit:
        try:
            links = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href,'/')]")
            
            for a in links:
                try:
                    href = a.get_attribute("href")
                    if href:
                        username = extract_username_from_url(href)
                        if username and username != profile:
                            following_users.add(username)
                except:
                    continue

            print(f"📢 Seguidos encontrados: {len(following_users)}/{limit}", end="\r")

            if len(following_users) >= limit:
                break

            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal)
            time.sleep(random.uniform(2.5, 4.0))

            new_scroll_position = driver.execute_script("return arguments[0].scrollTop", modal)

            if new_scroll_position == last_scroll_position:
                no_change_count += 1
                if no_change_count >= 5:
                    print("\n🛑 No hay más seguidos para cargar")
                    break
            else:
                no_change_count = 0
                last_scroll_position = new_scroll_position

        except Exception:
            time.sleep(2)

    print(f"\n✅ Lista de seguidos completada: {len(following_users)} usuarios")
    return following_users


def get_profile_info(driver, username, posts_to_extract=0):
    """
    Obtiene: followers, following, name, bio y username
    """
    try:
        url = INSTAGRAM_URLS['profile'].format(username=username)
        driver.get(url)
        human_delay(2, 4)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "header"))
        )

        follower_count = _get_followers_from_spans(driver)
        if follower_count is None: follower_count = _get_followers_from_meta(driver)
        if follower_count is None: follower_count = _get_followers_from_page_source(driver)

        following_count = _get_following_from_spans(driver)
        if following_count is None: following_count = _get_following_from_meta(driver)
        if following_count is None: following_count = _get_following_from_page_source(driver)

        full_name = _get_full_name(driver)
        bio_text = get_bio(driver)
        
        return {
            'username': username,
            'name': full_name,
            'followers': follower_count,
            'following': following_count,
            'bio': bio_text
        }

    except TimeoutException:
        return {'username': username, 'error': 'Timeout'}
    except Exception as e:
        return {'username': username, 'error': str(e)}


def collect_following_data(driver, usernames_set, max_profiles=None):
    """
    Recorre la lista de usernames y extrae sus detalles completos.
    """
    print("\n" + "=" * 60)
    print("📊 RECOPILANDO DETALLES DE 'SEGUIDOS'")
    print("=" * 60)

    detailed_data = []
    usernames_list = list(usernames_set)
    if max_profiles:
        usernames_list = usernames_list[:max_profiles]

    total = len(usernames_list)

    for index, username in enumerate(usernames_list, 1):
        print(f"[{index}/{total}] Procesando @{username}...")
        
        info = get_profile_info(driver, username)
        detailed_data.append(info)

        if index < total:
            human_delay(4, 7)

    print(f"\n✅ Detalles completados para {len(detailed_data)} perfiles")
    return detailed_data

