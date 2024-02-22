import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
import selenium.common.exceptions as S_Ex
from selenium.webdriver.common.by import By
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import bs4
import requests

m = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа',
     'сентября', 'октября', 'ноября', 'декабря']


def bs4_turn(seller, link):
    global m

    resp = requests.get(link)
    if resp.status_code == 200:
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        seller_link = soup.find('div', attrs={'data-name': "seller-block"}).find('a').get('href')
        if not seller:
            seller = soup.find('div', attrs={'data-name': "name_seller"}).get_text() + ' ' + seller_link
            if seller in vendors.keys():
                return None
            else:
                vendors[seller] = {}
        else:
            vendors[seller]['UPN'] = soup.find('div', class_="styles_seller-block__bottom-business-info__6bwR6").find('p').get_text().split(
                ': ')[1]
            vendors[seller]["positions"] = ('товаров:'+soup.find('p', class_="styles_seller-block__bottom-ads__cLriq").get_text().split(': ')[1])
        age = soup.find('p', class_="styles_seller-block__bottom-created-at__7lUQl").get_text().split(' ')[3:5]
        age[0] = age[0].replace(',', '')
        if age[0] in m:
            age[0] = str(m.index(age[0]) + 1)
        vendors[seller]['registered_on_kufar'] = age[0]+'.'+age[1]
        selenium_turn(seller, seller_link)
    else:
        print('Try again')


def selenium_turn(k, l):
    driver.switch_to.new_window('tab')
    driver.get(l)
    try:
        driver.find_element(By.XPATH, "//div[@data-type='shop_about']").click()
        driver.find_element(By.XPATH, "//button[@class='styles_button__RKUNo']").click() #extend info menu
        time.sleep(1)
        info = driver.find_element(By.XPATH, "//div[@data-testid='description_block']").text
    except S_Ex.NoSuchElementException:
        info = ''
    vendors[k]['info'] = info
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='link_block']")))
        site = driver.find_element(By.XPATH, "//div[@data-testid='link_block']//a").text
    except S_Ex.TimeoutException:
        if any(domain in k.lower() for domain in ['.by', '.ru', '.com', '.net']):
            site = "https://" + k.lower().split(' ')[-1]
        elif '.by' in info.lower() or '.ru' in info.lower() or '.com' in info.lower():
            words_list = info.lower().split(' ')
            for w in words_list:
                if '.by' in w or '.ru' in w or '.com' in w:
                    site = w
        else:
            site = ''
   # any(el in k.lower for el in [by,com])
    driver.close()
    driver.switch_to.window(window_name=driver.window_handles[0])


options = Options()
options.add_argument('start-maximized')
# options.add_argument('guest')
l = input('Вставьте ссылку на интересующую вас категорию товаров')

driver = webdriver.Edge(options=options)

driver.get(l)
driver.find_element(By.XPATH, "//div[@class='styles_buttons__fA69m']").click()
driver.find_element(By.XPATH, "//div[@class='styles_content__bm1fS']//button").click()

vendors = {}
nxt = True
n_lists = int(driver.find_elements(By.XPATH, "//a[@class='styles_link__8m3I9']")[-1].text)
for i in range(n_lists):
    elements = driver.find_elements(By.XPATH, "//div[@data-name='listings']//a[@class='styles_wrapper__5FoK7']")
    for e in elements:
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='link_block']")))
            element = e.find_element(By.XPATH,
                                     ".//span[@class='styles_secondary__MzdEb']").text.split(': ')[1].replace(r"''",
                                                                                                              "\"")
            if element not in vendors.keys():
                vendors[element] = {}
                link = e.get_attribute('href')
                bs4_turn(element, link)

        except S_Ex.TimeoutException:
            link = e.get_attribute('href')
            element = ''
            bs4_turn(element, link)
            pass

    if i < n_lists-1:
        nxt = driver.find_element(By.XPATH, "//a[@data-testid='generalist-pagination-next-link']")
        iframe = driver.find_element(By.TAG_NAME, "iframe")  #need this if opened in window?
        selenium.webdriver.ActionChains(driver)\
            .scroll_to_element(nxt)\
            .scroll_by_amount(0, 500)\
            .perform()
        time.sleep(1)
        nxt.click()
    time.sleep(3)
print(vendors)
input()


