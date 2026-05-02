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
    """Получение данных статей с главной страницы"""
    driver.get(URL)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-snippet')))

    article_cards = driver.find_elements(By.CSS_SELECTOR, 'div.article-snippet')
    articles_data = []

    for card in article_cards:
        try:
            # Заголовок и ссылка
            title_tag = card.find_element(By.CSS_SELECTOR, 'a.tm-title__link')
            title = title_tag.text
            link = title_tag.get_attribute('href')

            # Дата
            time_tag = card.find_element(By.TAG_NAME, 'time')
            date_str = time_tag.get_attribute('datetime')[:10]
            date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')

            # Текст превью
            try:
                lead_div = card.find_element(By.CSS_SELECTOR, 'div.lead')
                preview_div = lead_div.find_element(By.CSS_SELECTOR, 'div:nth-child(2)')
                preview_text = preview_div.text
            except Exception:
                preview_text = ""

            articles_data.append({
                'title': title,
                'link': link,
                'date': date,
                'preview_text': preview_text
            })

        except Exception:
            continue

    return articles_data


def get_full_text(driver, article_url):
    """Получение полного текста статьи по ссылке"""
    driver.get(article_url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#post-content-body')))

    try:
        body_element = driver.find_element(By.CSS_SELECTOR, '#post-content-body')
        return body_element.text
    except Exception:
        return ""


def contains_whole_word(text, word):
    """Проверка текста на точное совпадение слова"""
    if not text:
        return False

    # Экранируем спецсимволы в слове
    escaped_word = re.escape(word)

    pattern = rf'(?<![a-zа-яё0-9_\-]){escaped_word}(?![a-zа-яё0-9_\-])'

    return bool(re.search(pattern, text, re.IGNORECASE))


def check_keywords_in_text(text, keywords):
    """Проверка наличия ключевых слов в тексте, возвращает список найденных"""
    if not text:
        return []

    found = []
    for keyword in keywords:
        if contains_whole_word(text, keyword):
            found.append(keyword)
    return found


def main():
    """Основная функция"""
    driver = None

    try:
        driver = setup_driver()
        articles = get_articles_data(driver)

        results = []

        for article in articles:
            # Поиск в заголовке
            title_keywords = check_keywords_in_text(article['title'], KEYWORDS)

            if title_keywords:
                results.append(f"{article['date']} – {article['title']} – {article['link']}")
                continue

            # Поиск в превью
            preview_keywords = check_keywords_in_text(article['preview_text'], KEYWORDS)

            if preview_keywords:
                results.append(f"{article['date']} – {article['title']} – {article['link']}")
                continue

            # Поиск в полном тексте
            full_text = get_full_text(driver, article['link'])
            full_keywords = check_keywords_in_text(full_text, KEYWORDS)

            if full_keywords:
                results.append(f"{article['date']} – {article['title']} – {article['link']}")
            # if full_keywords:
            #     results.append(f"{article['date']} – {article['title']} – {article['link']} [найдено в полном тексте]")

            # Задержка между запросами
            time.sleep(0.5)

        # Вывод результатов
        if results:
            print('\n'.join(results))

    except Exception:
        pass

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()