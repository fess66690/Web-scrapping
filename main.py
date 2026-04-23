from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ключевые слова для поиска
KEYWORDS = ['Нанотехнологии', 'Карьера в IT-индустрии', 'Программирование', 'python']

# URL страницы со свежими статьями
URL = 'https://habr.com/ru/articles/'


def setup_driver():
    """Настройка и запуск браузера Chrome в headless-режиме"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Фоновый режим без открытия окна браузера
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def get_articles_list(driver):
    """Получение списка статей с главной страницы"""
    driver.get(URL)

    # Ожидаем загрузки хотя бы одной статьи (максимум 10 секунд)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

    # Возвращаем все найденные статьи
    return driver.find_elements(By.TAG_NAME, 'article')


def extract_article_info(article):
    """Извлечение заголовка, ссылки, даты"""
    # Заголовок и ссылка
    title_tag = article.find_element(By.CSS_SELECTOR, 'a.tm-title__link')
    title = title_tag.text
    link = title_tag.get_attribute('href')

    # Дата публикации
    time_tag = article.find_element(By.TAG_NAME, 'time')
    date_str = time_tag.get_attribute('datetime')[:10]
    date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')

    # Теги статьи
    try:
        hub_elements = article.find_elements(By.CSS_SELECTOR, '.tm-publication-hub__link')
        hubs_text = ' '.join([
            hub.text.replace('*', '').strip()
            for hub in hub_elements
        ])
    except Exception:
        hubs_text = ""

    return {
        'title': title,
        'link': link,
        'date': date,
        'hubs_text': hubs_text
    }


def check_keywords_match(preview_text, keywords):
    """Проверка наличия ключевых слов в тексте превью"""
    preview_lower = preview_text.lower()
    return [
        keyword for keyword in keywords
        if keyword.lower() in preview_lower
    ]


def main():
    """Основная функция"""
    driver = None

    try:
        # Инициализация драйвера
        driver = setup_driver()

        # Получение списка статей
        articles = get_articles_list(driver)
        print(f"Проанализировано статей: {len(articles)}")

        results = []

        # Обрабатываем необходимое количество статей
        quantity_articles = 20
        for article in articles[:quantity_articles]:
            # Извлекаем информацию из карточки
            info = extract_article_info(article)

            # Формируем текст для поиска (заголовок + хабы)
            preview_text = f"{info['title']} {info['hubs_text']}"

            # Проверяем наличие ключевых слов
            matched_keywords = check_keywords_match(preview_text, KEYWORDS)

            if matched_keywords:
                results.append(
                    f"{info['date']} – {info['title']} – {info['link']}"
                )

        # Вывод результатов
        if results:
            print("\nНайденные статьи:")
            print("-" * 80)
            print('\n'.join(results))
        else:
            print("Статей, соответствующих ключевым словам, не найдено.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Закрытие браузера
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()