import requests
import os

def download_font():
    # URL шрифта с сайта vidi-design.ru
    font_url = 'https://vidi-design.ru/static/fonts/normalidad-text.woff2'
    
    # Путь для сохранения
    font_path = 'vidi-design.ru/static/fonts/normalidad-text.woff2'
    
    # Создаем директорию, если её нет
    os.makedirs(os.path.dirname(font_path), exist_ok=True)
    
    try:
        # Загружаем шрифт
        response = requests.get(font_url)
        response.raise_for_status()
        
        # Сохраняем файл
        with open(font_path, 'wb') as f:
            f.write(response.content)
            
        print(f'Шрифт успешно загружен в {font_path}')
    except Exception as e:
        print(f'Ошибка при загрузке шрифта: {e}')

if __name__ == '__main__':
    download_font() 