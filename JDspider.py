'''
Name:JDspider.py
Date:2019/7/10
Author:mac
Email:1109920082@qq.com
Desc:
'''
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 20)


def search():
    try:
        browser.get('https://www.jd.com')
        # 判断浏览器是否加载成功
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button > i"))
        )
        input.send_keys("美食")
        submit.click()
        total_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b")))
        return total_page.text
    except TimeoutException:
        return search()


def next_page(page_num):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > a"))
        )
        browser.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")  # 将窗口滑动到最底部
        input.clear()
        input.send_keys(page_num)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_num)))

    except TimeoutException:
        next_page(page_num)


def main():
    total_page = search()
    print(total_page)
    for i in range(2, int(total_page) + 1):
        next_page(i)


if __name__ == '__main__':
    main()
