import json
from time import sleep
import re

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

options = ChromeOptions()
options.add_argument('--headless')


def wait_element(browser, delay=5, by=By.CSS_SELECTOR, value=None):
    return WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((by, value))
    )


def contains_whole_word(text, word):
    """Проверяем точное совпадение целого слова без учета регистра"""
    if not text:
        return False

    escaped_word = re.escape(word)

    pattern = rf'(?<![a-zа-яё0-9_\-]){escaped_word}(?![a-zа-яё0-9_\-])'
    return bool(re.search(pattern, text, re.IGNORECASE))


def check_keywords_in_text(text, keywords):
    """Проверяем наличие ключевых слов в тексте"""
    if not text:
        return []

    found = []
    for keyword in keywords:
        if contains_whole_word(text, keyword):
            found.append(keyword)
    return found


driver = Chrome(options=options)
driver.get('https://habr.com/ru/articles/')

articles_block = wait_element(driver, value='div.tm-articles-list')

articles_list = articles_block.find_elements(By.CSS_SELECTOR, value='article')

parsed_data = []
results = []

for article in articles_list:

    div_with_link = wait_element(article, value='h2')

    link = wait_element(div_with_link, value='a').get_attribute('href')
    header = wait_element(article, value='h2').text.strip()
    time = wait_element(article, value='time').get_attribute('title')
    text = wait_element(article, value='div.article-formatted-body').text.strip()
    parsed_data.append({
        'header': header,
        'link': link,
        'time': time,
        'text': text,
    })

    matched_keywords = check_keywords_in_text(header, KEYWORDS) or check_keywords_in_text(text, KEYWORDS)

    if matched_keywords:
        results.append(f"{time} – {header} – {link}")

# Вывод результатов в требуемом формате
if results:
    print('\n'.join(results))
else:
    print("Статей, соответствующих ключевым словам, не найдено.")
#
# with open('output.json', 'w', encoding='utf-8') as file:
#     json.dump(parsed_data, file, ensure_ascii=False, indent=2)
