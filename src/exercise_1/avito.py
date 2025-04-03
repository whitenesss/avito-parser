import os
import time
import random
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class AvitoParser:
    def __init__(self, base_url, output_dir="output"):
        print(f"Инициализация парсера для {base_url}")
        self.base_url = base_url
        self.output_dir = output_dir
        self.driver = self._init_driver()
        self.parsed_ads = set()
        os.makedirs(output_dir, exist_ok=True)
        print(f"Выходная директория: {os.path.abspath(output_dir)}")

    def _init_driver(self):
        """Инициализация ChromeDriver с настройками для обхода защиты"""
        chrome_options = Options()

        # Настройки для маскировки под обычный браузер
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Инициализация драйвера
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Маскировка WebDriver
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                window.navigator.chrome = {
                    runtime: {},
                };
            """
        })
        return driver

    def _random_delay(self, min_sec=2, max_sec=5):
        """Случайная задержка между действиями"""
        delay = random.uniform(min_sec, max_sec)
        print(f"Ожидание {delay:.2f} сек...")
        time.sleep(delay)

    def parse_page(self, url):
        """Загрузка и парсинг страницы с объявлениями"""
        print(f"Загрузка страницы: {url}")
        try:
            self.driver.get(url)
            self._random_delay(3, 7)

            # Проверка на капчу
            if self._check_captcha():
                print("Обнаружена капча! Попробуйте:")
                print("1. Вручную решить капчу в браузере")
                print("2. Сменить IP-адрес")
                print("3. Подождать 10-15 минут")
                input("Нажмите Enter после решения капчи...")

            # Ожидание загрузки объявлений
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="item"]')))

            return self.driver.page_source
        except Exception as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None

    def _check_captcha(self):
        """Проверка наличия капчи на странице"""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "div.captcha__container").is_displayed()
        except:
            return False

    def extract_ads(self, html):
        """Извлечение данных объявлений из HTML"""
        print("Извлечение объявлений...")
        soup = BeautifulSoup(html, 'html.parser')
        ads = []

        ad_cards = soup.select('div[data-marker="item"]')
        print(f"Найдено карточек: {len(ad_cards)}")

        for i, card in enumerate(ad_cards, 1):
            try:
                print(f"\nОбработка карточки #{i}")

                title = card.select_one('[itemprop="name"]').text.strip()
                print(f"Заголовок: {title[:30]}...")

                ads.append({
                    'title': title,
                    'price': card.select_one('[itemprop="price"]')['content'],
                    'address': card.select_one('[data-marker="item-address"]').text.strip(),
                    'area': self._extract_area(card),
                    'link': urljoin(self.base_url, card.select_one('a[itemprop="url"]')['href']),
                    'date': card.select_one('[data-marker="item-date"]').text.strip()
                })

            except Exception as e:
                print(f"Ошибка в карточке #{i}: {e}")
                continue

        return ads

    def _extract_area(self, card):
        """Извлечение площади помещения"""
        try:
            params = card.select_one('[data-marker="item-specific-params"]').text
            return next(p.split('м²')[0].strip()
                        for p in params.split(',')
                        if 'м²' in p)
        except:
            return "0"

    def save_to_xml(self, ads, file_index):
        """Сохранение объявлений в XML файл"""
        filename = os.path.join(self.output_dir, f"ads_{file_index}.xml")
        print(f"Сохранение {len(ads)} объявлений в {filename}")

        root = ET.Element("ads")
        for ad in ads:
            ad_elem = ET.SubElement(root, "ad")
            for key, value in ad.items():
                child = ET.SubElement(ad_elem, key)
                child.text = str(value)

        ET.ElementTree(root).write(filename, encoding='utf-8', xml_declaration=True)

    def run(self, max_ads=50, ads_per_file=20):
        """Основной метод запуска парсера"""
        print(f"\nЗапуск парсера (макс. {max_ads} объявлений)")
        total_ads = 0
        page = 1

        try:
            while total_ads < max_ads:
                print(f"\nСтраница {page}:")
                html = self.parse_page(f"{self.base_url}&p={page}")

                if not html:
                    print("Не удалось получить данные, завершение")
                    break

                ads = self.extract_ads(html)
                if not ads:
                    print("Объявления не найдены, завершение")
                    break

                self.save_to_xml(ads, page)
                total_ads += len(ads)
                page += 1
                self._random_delay(5, 10)

            print(f"\nГотово! Всего собрано {total_ads} объявлений")
        finally:
            self.driver.quit()


if __name__ == "__main__":
    url = "https://www.avito.ru/rostovskaya_oblast/kvartiry/prodam-ASgBAgICAUSSA8YQ?district=43"
    parser = AvitoParser(url, )
    parser.run(max_ads=20)