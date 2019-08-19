'''
Name:taobao_spider.py
Date:2019/7/10
Author:mac
Email:1109920082@qq.com
Desc:
'''
import re
import time

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 20)


def search():
    try:
        browser.get('https://www.taobao.com')
        # 判断浏览器是否加载成功
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        )
        input.send_keys(KEYWORD)
        submit.click()
        time.sleep(2)
        total_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total")))
        # 在网页完全加载后标志显示后，获取其信息
        get_products()
        return total_page.text
    except TimeoutException:
        return search()


def next_page(page_num):
    try:
        # 获取输入页码框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        # 获取确定按钮
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        # browser.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")  # 将窗口滑动到最底部
        input.clear()
        input.send_keys(page_num)
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_num)))
        # 在网页完全加载后标志显示后，获取其信息
        get_products()
    except TimeoutException:
        next_page(page_num)


# 获取商品信息
def get_products():
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".m-itemlist .items .item"))
    )
    # 得到网页源代码
    html = browser.page_source
    # 使用pyquery解析
    doc = pq(html)
    items = doc(".m-itemlist .items .item").items()
    for i in items:
        product = {
            'image': i.find('.pic .img').attr('src'),
            'price': i.find('.price').text(),
            'deal': i.find('.deal-cnt').text()[:-3],
            'title': i.find('.title').text(),
            'shop': i.find('.shop').text(),
            'location': i.find('.location').text()
        }
        print(product)
        save_to_Mongo(product)


# 将数据存储到MongoDB
def save_to_Mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("Mongo数据存储成功", result)
    except Exception:
        print("存储到MongoDB失败", result)


def main():
    # 异常处理
    try:
        total_page = search()
        total = int(re.compile('(\d+)').search(total_page).group(1))
        print(total)
        for i in range(2, 10):
            next_page(i)
    except Exception:
        print('出错了')
    finally:
        browser.close()

if __name__ == '__main__':
    main()
