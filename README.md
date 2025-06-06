# Клонирование сайта vidi-design.ru

Этот скрипт позволяет клонировать сайт vidi-design.ru с обходом защиты Cloudflare.

## Требования

- Python 3.8 или выше
- Установленные зависимости из requirements.txt

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Установите браузеры для Playwright:
```bash
playwright install
```

## Использование

1. Запустите скрипт:
```bash
python scraper.py
```

2. Дождитесь завершения процесса. Все файлы будут сохранены в директории с именем домена сайта.

## Особенности

- Использует Playwright для обхода защиты Cloudflare
- Сохраняет все HTML страницы
- Скачивает CSS, JavaScript и изображения
- Сохраняет структуру директорий сайта
- Игнорирует PDF и DOC файлы
- Использует реалистичные заголовки браузера

## Примечания

- Скрипт может работать медленно из-за задержек для обхода защиты
- Некоторые динамически загружаемые элементы могут не сохраниться
- Рекомендуется запускать скрипт на компьютере с хорошим интернет-соединением 