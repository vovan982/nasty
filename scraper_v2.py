from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import time
import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
import logging
import re
from typing import Set, List
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class WebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls: Set[str] = set()
        self.resources_to_download: Set[str] = set()
        self.missing_files: Set[str] = set()
        self.load_progress()
        
    def load_progress(self):
        """Загрузка прогресса из файла"""
        try:
            if os.path.exists('progress.json'):
                with open('progress.json', 'r') as f:
                    data = json.load(f)
                    self.visited_urls = set(data.get('visited_urls', []))
                    self.resources_to_download = set(data.get('resources', []))
            logging.info(f"Загружено {len(self.visited_urls)} посещенных URL и {len(self.resources_to_download)} ресурсов")
        except Exception as e:
            logging.error(f"Ошибка при загрузке прогресса: {e}")
            
    def save_progress(self):
        """Сохранение прогресса в файл"""
        try:
            with open('progress.json', 'w') as f:
                json.dump({
                    'visited_urls': list(self.visited_urls),
                    'resources': list(self.resources_to_download)
                }, f)
        except Exception as e:
            logging.error(f"Ошибка при сохранении прогресса: {e}")
            
    def create_directory_structure(self):
        """Создание структуры директорий для сохранения файлов"""
        if not os.path.exists(self.domain):
            os.makedirs(self.domain)
            
    def sanitize_filename(self, filename):
        """Очистка имени файла от недопустимых символов"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
            
    def save_page(self, url, content):
        """Сохранение HTML страницы"""
        try:
            path = urlparse(url).path
            if not path or path == '/':
                path = '/index.html'
                
            path = path.split('#')[0].split('?')[0]
            filename = os.path.basename(path) or 'index.html'
            filename = self.sanitize_filename(filename)
            
            dir_path = os.path.dirname(path)
            file_path = os.path.join(self.domain, dir_path.lstrip('/'), filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Исправляем пути к ресурсам в HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Исправляем пути в тегах link
            for link in soup.find_all('link'):
                if link.get('href'):
                    href = link['href']
                    if not href.startswith(('http://', 'https://')):
                        link['href'] = href.lstrip('/')
            
            # Исправляем пути в тегах script
            for script in soup.find_all('script'):
                if script.get('src'):
                    src = script['src']
                    if not src.startswith(('http://', 'https://')):
                        script['src'] = src.lstrip('/')
            
            # Исправляем пути в тегах img
            for img in soup.find_all('img'):
                if img.get('src'):
                    src = img['src']
                    if not src.startswith(('http://', 'https://')):
                        img['src'] = src.lstrip('/')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            logging.info(f"Сохранена страница: {file_path}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении страницы {url}: {e}")
            
    async def download_resource(self, session, url):
        """Скачивание одного ресурса"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    path = urlparse(url).path.split('?')[0]
                    filename = self.sanitize_filename(os.path.basename(path))
                    dir_path = os.path.dirname(path)
                    file_path = os.path.join(self.domain, dir_path.lstrip('/'), filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    content = await response.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logging.info(f"Скачан ресурс: {file_path}")
                    return True
        except Exception as e:
            logging.error(f"Ошибка при скачивании {url}: {e}")
        return False
            
    async def download_resources(self):
        """Параллельное скачивание всех ресурсов"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in self.resources_to_download:
                tasks.append(self.download_resource(session, url))
            
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for r in results if r)
            logging.info(f"Успешно скачано {success_count} из {len(results)} ресурсов")
            
    def create_service_files(self):
        """Создание необходимых сервисных файлов"""
        try:
            # Создаем flutter_service_worker.js
            service_worker_path = os.path.join(self.domain, 'flutter_service_worker.js')
            os.makedirs(os.path.dirname(service_worker_path), exist_ok=True)
            with open(service_worker_path, 'w') as f:
                f.write('''
// Service worker for Flutter web app
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('flutter-app-cache').then(function(cache) {
            return cache.addAll([]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
''')
            logging.info(f"Создан файл: {service_worker_path}")
            
            # Создаем favicon.ico
            favicon_path = os.path.join(self.domain, 'favicon.ico')
            os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
            with open(favicon_path, 'wb') as f:
                # Пустой favicon
                f.write(b'')
            logging.info(f"Создан файл: {favicon_path}")
            
            # Создаем .htaccess для правильной обработки путей
            htaccess_path = os.path.join(self.domain, '.htaccess')
            with open(htaccess_path, 'w') as f:
                f.write('''
RewriteEngine On
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [L,QSA]
''')
            logging.info(f"Создан файл: {htaccess_path}")
        except Exception as e:
            logging.error(f"Ошибка при создании сервисных файлов: {e}")
            raise  # Перебрасываем исключение для лучшей диагностики
            
    def check_missing_files(self):
        """Проверка отсутствующих файлов"""
        # Проверяем основные файлы
        required_files = [
            'flutter_service_worker.js',
            'favicon.ico',
            '.htaccess'
        ]
        
        for file in required_files:
            if not os.path.exists(os.path.join(self.domain, file)):
                self.missing_files.add(file)
                logging.info(f"Отсутствует файл: {file}")
                
        # Проверяем HTML файлы
        html_files = [
            'index.html',
            'aboutme',
            'blog',
            'contact',
            'faqs',
            'home',
            'privacy',
            'sitemap',
            'services/index.html'
        ]
        
        for file in html_files:
            if not os.path.exists(os.path.join(self.domain, file)):
                self.missing_files.add(file)
                logging.info(f"Отсутствует файл: {file}")
                
        # Проверяем директории
        required_dirs = [
            'services',
            'assets',
            'images'
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(self.domain, dir_name)):
                self.missing_files.add(dir_name)
                logging.info(f"Отсутствует директория: {dir_name}")
                
    def fix_broken_files(self):
        """Исправление битых файлов"""
        try:
            # Исправляем HTML файлы
            for root, _, files in os.walk(self.domain):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                soup = BeautifulSoup(content, 'html.parser')
                                
                                # Исправляем пути в тегах link
                                for link in soup.find_all('link'):
                                    if link.get('href'):
                                        href = link['href']
                                        if not href.startswith(('http://', 'https://')):
                                            link['href'] = href.lstrip('/')
                                
                                # Исправляем пути в тегах script
                                for script in soup.find_all('script'):
                                    if script.get('src'):
                                        src = script['src']
                                        if not src.startswith(('http://', 'https://')):
                                            script['src'] = src.lstrip('/')
                                
                                # Исправляем пути в тегах img
                                for img in soup.find_all('img'):
                                    if img.get('src'):
                                        src = img['src']
                                        if not src.startswith(('http://', 'https://')):
                                            img['src'] = src.lstrip('/')
                                
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(str(soup))
                            logging.info(f"Исправлен файл: {file_path}")
                        except Exception as e:
                            logging.error(f"Ошибка при исправлении файла {file_path}: {e}")
        except Exception as e:
            logging.error(f"Ошибка при исправлении файлов: {e}")
            
    async def process_page(self, url):
        """Обработка страницы и извлечение всех ссылок"""
        if url in self.visited_urls:
            return
            
        logging.info(f"Обработка страницы: {url}")
        self.visited_urls.add(url)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
            })
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                html = await page.content()
                self.save_page(url, html)
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Собираем все ссылки
                for link in soup.find_all(['a', 'link', 'script', 'img']):
                    href = link.get('href') or link.get('src')
                    if href:
                        full_url = urljoin(url, href)
                        if self.domain in full_url:
                            if any(ext in full_url.lower() for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']):
                                self.resources_to_download.add(full_url)
                            elif not any(ext in full_url.lower() for ext in ['.pdf', '.doc', '.docx']):
                                await self.process_page(full_url)
                                
            except Exception as e:
                logging.error(f"Ошибка при обработке {url}: {e}")
                
            finally:
                await browser.close()
                self.save_progress()
                
    async def start(self):
        """Запуск процесса клонирования"""
        logging.info("Проверка отсутствующих файлов...")
        self.check_missing_files()
        
        if not self.missing_files:
            logging.info("Все файлы присутствуют, исправляем ошибки...")
            self.fix_broken_files()
            return
            
        logging.info(f"Найдено {len(self.missing_files)} отсутствующих файлов")
        self.create_directory_structure()
        
        # Скачиваем только отсутствующие файлы
        for file in self.missing_files:
            if file.endswith(('.html', '')):  # HTML файлы или директории
                url = urljoin(self.base_url, file)
                await self.process_page(url)
            elif file in ['flutter_service_worker.js', 'favicon.ico', '.htaccess']:
                self.create_service_files()
                
        # Скачиваем ресурсы для новых страниц
        if self.resources_to_download:
            logging.info(f"Скачиваем {len(self.resources_to_download)} ресурсов...")
            await self.download_resources()
            
        logging.info("Клонирование завершено!")

async def main():
    scraper = WebsiteScraper("https://vidi-design.ru")
    await scraper.start()

if __name__ == "__main__":
    asyncio.run(main()) 