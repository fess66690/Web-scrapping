import re
import time
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


def get_articles_data(driver):
    """Получение данных статей с главной страницы."""
    driver.get(URL)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

    # Ждём загрузки контента
    time.sleep(2)

    # Находим все карточки статей
    article_cards = driver.find_elements(By.TAG_NAME, 'article')

    articles_data = []

    for card in article_cards[:10]:  # Берём первые 10 статей
        try:
            # Извлекаем заголовок и ссылку
            title_tag = card.find_element(By.CSS_SELECTOR, 'a.tm-title__link')
            title = title_tag.text
            link = title_tag.get_attribute('href')

            # Извлекаем дату
            time_tag = card.find_element(By.TAG_NAME, 'time')
            date_str = time_tag.get_attribute('datetime')[:10]
            date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')

            # Извлекаем текст превью
            try:
                preview_element = card.find_element(By.CSS_SELECTOR, 'div.article-formatted-body')
                preview_text = preview_element.text
            except Exception:
                preview_text = ""

            articles_data.append({
                'title': title,
                'link': link,
                'date': date,
                'preview_text': preview_text
            })

        except Exception as e:
            # Пропускаем проблемные карточки
            continue

    return articles_data


def get_full_text(driver, article_url):
    """Получение полного текста статьи по ссылке"""
    driver.get(article_url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-formatted-body')))

    try:
        body_element = driver.find_element(By.CSS_SELECTOR, 'div.article-formatted-body')
        return body_element.text
    except Exception:
        return ""


def contains_whole_word(text, word):
    """Проверяет, содержит ли текст точное совпадение слова без учета регистра"""
    if not text:
        return False

    escaped_word = re.escape(word)
    pattern = rf'(?<![а-яА-Яa-zA-Z]){escaped_word}(?![а-яА-Яa-zA-Z])'
    return bool(re.search(pattern, text, re.IGNORECASE))


def check_keywords_match(title, preview_text, full_text, keywords):
    """Проверка наличия ключевых слов в заголовке, превью или полном тексте"""
    matched = []

    for keyword in keywords:
        if (contains_whole_word(title, keyword) or
            contains_whole_word(preview_text, keyword) or
            contains_whole_word(full_text, keyword)):
            matched.append(keyword)

    return matched


def main():
    """Основная функция"""
    driver = None

    try:
        driver = setup_driver()

        # Получаем данные статей (избегая stale reference)
        articles = get_articles_data(driver)
        results = []

        for idx, article in enumerate(articles, 1):
            # Сначала проверяем заголовок и превью
            quick_matched = check_keywords_match(
                article['title'],
                article['preview_text'],
                "",
                KEYWORDS
            )

            if quick_matched:
                results.append(f"{article['date']} – {article['title']} – {article['link']}")
            else:
                # Загружаем полный текст
                full_text = get_full_text(driver, article['link'])
                full_matched = check_keywords_match(
                    article['title'],
                    article['preview_text'],
                    full_text,
                    KEYWORDS
                )

                if full_matched:
                    results.append(f"{article['date']} – {article['title']} – {article['link']}")

                time.sleep(0.5)

        # Вывод результатов
        if results:
            print('\n'.join(results))

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()