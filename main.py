import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ключевые слова для поиска (строго по заданию)
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL страницы со свежими статьями
URL = 'https://habr.com/ru/articles/'


def setup_driver():
    """Настройка и запуск браузера Chrome в headless-режиме"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def get_articles_list(driver):
    """Получение списка статей с главной страницы"""
    driver.get(URL)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

    return driver.find_elements(By.TAG_NAME, 'article')


def extract_article_info(article):
    """Извлечение заголовка, ссылки, даты и текста превью из карточки статьи"""
    # Заголовок и ссылка
    title_tag = article.find_element(By.CSS_SELECTOR, 'a.tm-title__link')
    title = title_tag.text
    link = title_tag.get_attribute('href')

    # Дата публикации
    time_tag = article.find_element(By.TAG_NAME, 'time')
    date_str = time_tag.get_attribute('datetime')[:10]
    date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')

    # Текст превью
    try:
        preview_element = article.find_element(By.CSS_SELECTOR, 'div.article-formatted-body')
        preview_text = preview_element.text
    except Exception:
        preview_text = ""

    return {
        'title': title,
        'link': link,
        'date': date,
        'preview_text': preview_text
    }


def contains_whole_word(text, word):
    """Проверяет, содержит ли текст точное совпадение слова без учета регистра"""
    if not text:
        return False

    # Экранируем специальные символы в слове
    escaped_word = re.escape(word)

    # Границы слова: начало строки, пробел, пунктуация или конец строки
    pattern = rf'(?<![а-яА-Яa-zA-Z]){escaped_word}(?![а-яА-Яa-zA-Z])'

    return bool(re.search(pattern, text, re.IGNORECASE))


def check_keywords_match(title, preview_text, keywords):
    """Проверка наличия ключевых слов в заголовке или превью"""
    title_lower = title.lower()
    preview_lower = preview_text.lower() if preview_text else ""

    matched = []
    for keyword in keywords:
        if contains_whole_word(title_lower, keyword) or contains_whole_word(preview_lower, keyword):
            matched.append(keyword)

    return matched


def main():
    """Основная функция"""
    driver = None

    try:
        driver = setup_driver()

        articles = get_articles_list(driver)

        results = []

        for article in articles[:10]:
            info = extract_article_info(article)

            # Проверяем наличие ключевых слов (точные совпадения)
            matched_keywords = check_keywords_match(
                info['title'],
                info['preview_text'],
                KEYWORDS
            )

            if matched_keywords:
                results.append(
                    f"{info['date']} – {info['title']} – {info['link']}"
                )

        # Вывод
        if results:
            print('\n'.join(results))

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()