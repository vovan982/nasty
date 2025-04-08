from playwright.sync_api import sync_playwright
import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class SiteDownloader:
    def __init__(self, base_url, output_dir):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.session = requests.Session()
        
        # Настройка заголовков для эмуляции браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def setup_playwright(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Переходим на сайт и ждем загрузки
            page.goto(self.base_url, wait_until='networkidle')
            
            # Получаем куки после успешной загрузки
            cookies = context.cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # Получаем HTML после обработки JavaScript
            html = page.content()
            
            # Сохраняем главную страницу
            self.save_file('index.html', html)
            
            # Находим все ссылки на странице
            links = page.query_selector_all('a')
            for link in links:
                href = link.get_attribute('href')
                if href and not href.startswith('#'):
                    full_url = urljoin(self.base_url, href)
                    if self.is_valid_url(full_url):
                        self.download_page(full_url)
            
            browser.close()

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.netloc == urlparse(self.base_url).netloc and url not in self.visited_urls

    def save_file(self, path, content):
        full_path = os.path.join(self.output_dir, path)
        dir_path = os.path.dirname(full_path)
        
        # Создаем директорию, если она не существует
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # Если путь указывает на директорию, добавляем index.html
        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, 'index.html')
        
        # Сохраняем файл
        try:
            if isinstance(content, str):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(full_path, 'wb') as f:
                    f.write(content)
        except Exception as e:
            print(f"Error saving file {full_path}: {str(e)}")

    def download_page(self, url):
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        print(f"Downloading: {url}")
        
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                # Сохраняем HTML
                path = urlparse(url).path.lstrip('/')
                if not path:
                    path = 'index.html'
                elif path.endswith('/'):
                    path = os.path.join(path, 'index.html')
                self.save_file(path, response.text)
                
                # Парсим HTML для поиска ресурсов
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Скачиваем CSS
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href:
                        self.download_resource(href)
                
                # Скачиваем JavaScript
                for script in soup.find_all('script', src=True):
                    self.download_resource(script['src'])
                
                # Скачиваем изображения
                for img in soup.find_all('img', src=True):
                    self.download_resource(img['src'])
                
                # Скачиваем шрифты
                for font in soup.find_all('link', rel='preload', as_='font'):
                    href = font.get('href')
                    if href:
                        self.download_resource(href)
                
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")

    def download_resource(self, url):
        if not url or url.startswith('data:'):
            return
            
        full_url = urljoin(self.base_url, url)
        if not self.is_valid_url(full_url):
            return
            
        try:
            response = self.session.get(full_url, headers=self.headers)
            if response.status_code == 200:
                path = urlparse(full_url).path.lstrip('/')
                self.save_file(path, response.content)
        except Exception as e:
            print(f"Error downloading resource {url}: {str(e)}")

def main():
    base_url = "https://vidi-design.ru/services"
    output_dir = "vidi-design.ru"
    
    downloader = SiteDownloader(base_url, output_dir)
    downloader.setup_playwright()

if __name__ == "__main__":
    main() 