"""
Archivo: scrape_followers.py
Descripción: Descarga SEGUIDOS y exporta a Excel
"""

import pandas as pd
from browser import init_browser
from auth import InstagramAuth
from scraper import scrape_following, collect_following_data
from config import RESULTS_DIR
from utils import human_delay


def main():
    print("\n" + "="*60)
    print("INSTAGRAM FOLLOWING SCRAPER - EXPORTACIÓN A EXCEL")
    print("="*60 + "\n")

    # Iniciar navegador
    driver = init_browser()

    # Crear instancia de autenticación
    auth = InstagramAuth(driver)

    # Cargar credenciales (método estático)
    username, password = InstagramAuth.load_credentials()

    try:
        # ------------------ AUTENTICACIÓN ------------------
        print("🔐 Autenticando...")
        cookies_loaded = auth.load_cookies()

        if not cookies_loaded:
            print("📝 Login manual requerido...")
            if not auth.login(username, password):
                print("❌ Login fallido")
                return
        else:
            driver.get("https://www.instagram.com/")
            human_delay(3, 4)

            if not auth.verify_session():
                print("🔄 Cookies inválidas, reintentando login...")
                if not auth.login(username, password):
                    print("❌ Login fallido")
                    return

        # ------------------ INPUTS ------------------
        profile = input("👤 Username objetivo: ").strip()
        limit = int(input("🔢 Límite de seguidos a extraer: "))

        # ------------------ FASE 1 ------------------
        print("\n📌 Extrayendo lista de seguidos...")
        following_users = scrape_following(driver, profile, limit)

        if not following_users:
            print("❌ No se encontraron seguidos.")
            return

        # ------------------ FASE 2 ------------------
        print("\n📊 Extrayendo datos de cada perfil...")
        data = collect_following_data(driver, following_users, max_profiles=limit)

        # ------------------ EXPORTAR A EXCEL ------------------
        df = pd.DataFrame(data)

        excel_file = RESULTS_DIR / f"seguidos_{profile}.xlsx"
        df.to_excel(excel_file, index=False)

        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print(f"📁 Archivo generado: {excel_file}")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        input("\nPresiona ENTER para cerrar...")
        driver.quit()


if __name__ == "__main__":
    main()
