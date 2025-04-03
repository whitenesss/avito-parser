import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import time
from urllib.parse import urljoin


class AvitoParser:
    def __init__(self, base_url, output_dir="output"):
        print(f"Инициализация парсера для {base_url}")
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.parsed_ads = set()
        os.makedirs(output_dir, exist_ok=True)
        print(f"Выходная директория: {os.path.abspath(output_dir)}")

    def parse_page(self, url):
        print(f"Загрузка страницы: {url}")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            print(f"Статус ответа: {response.status_code}")
            return response.text
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def extract_ads(self, html):
        print("Извлечение объявлений...")
        soup = BeautifulSoup(html, 'html.parser')
        ads = []

        # Актуальные селекторы для Avito (может потребоваться обновление)
        ad_cards = soup.select('div[data-marker="item"]')
        print(f"Найдено карточек: {len(ad_cards)}")

        for i, card in enumerate(ad_cards, 1):
            try:
                # Добавьте отладочную печать для каждой карточки
                print(f"\nОбработка карточки #{i}")

                title = card.select_one('[itemprop="name"]').text.strip()
                print(f"Заголовок: {title[:30]}...")

                ads.append({
                    'title': title,
                    'price': card.select_one('[itemprop="price"]')['content'],
                    'address': card.select_one('[data-marker="item-address"]').text.strip(),
                    'area': self.extract_area(card),
                    'link': urljoin(self.base_url, card.select_one('a[itemprop="url"]')['href']),
                    'date': card.select_one('[data-marker="item-date"]').text.strip()
                })

            except Exception as e:
                print(f"Ошибка в карточке #{i}: {e}")
                continue

        return ads

    def extract_area(self, card):
        try:
            params = card.select_one('[data-marker="item-specific-params"]').text
            return next(p.split('м²')[0].strip()
                        for p in params.split(',')
                        if 'м²' in p)
        except:
            return "0"

    def save_to_xml(self, ads, file_index):
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
        print(f"\nЗапуск парсера (макс. {max_ads} объявлений)")
        total_ads = 0
        page = 1

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
            time.sleep(1)

        print(f"\nГотово! Всего собрано {total_ads} объявлений")


if __name__ == "__main__":

    url = "https://www.avito.ru/rostovskaya_oblast/kvartiry/prodam-ASgBAgICAUSSA8YQ?district=45"
    parser = AvitoParser(url)
    parser.run(max_ads=50)