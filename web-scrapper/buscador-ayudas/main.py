import json, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
driver.get("https://comercio.gob.es/comerciointerior/actuaciones_competitividad/paginas/buscadorayudas.aspx")
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.convocatorias ul li")))

results = []

while True:
    current = int(driver.find_element(By.CSS_SELECTOR, "ul.pagination.bootpag li.active").get_attribute("data-lp"))
    items = driver.find_elements(By.CSS_SELECTOR, "div.convocatorias ul li")
    for item in items:
        title = item.find_element(By.CSS_SELECTOR, "h2.titulo").text
        try:
            source = item.find_element(By.XPATH,
                                       ".//p[starts-with(normalize-space(strong),'Base reguladora')]/a").get_attribute(
                "href")
        except:
            source = ""


        def gt(xpath):
            try:
                return item.find_element(By.XPATH, xpath).text
            except:
                return ""


        date_from = gt(".//dt[.='Desde:']/following-sibling::dd[1]")
        date_to = gt(".//dt[.='Hasta:']/following-sibling::dd[1]")
        scope = gt(".//dt[.='Ambito:']/following-sibling::dd[1]")
        theme = gt(".//dt[.='Temática:']/following-sibling::dd[1]")

        if title == "":
            continue

        results.append({
            "title": title,
            "source": source,
            "date": {"from": date_from, "to": date_to},
            "scope": scope,
            "theme": theme
        })

    if current >= 30:
        break

    pag_next_li = driver.find_element(By.CSS_SELECTOR, "ul.pagination.bootpag li.next")
    a = pag_next_li.find_element(By.TAG_NAME, "a")

    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", a)
        a.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", a)

    wait.until(EC.staleness_of(items[0]))
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.convocatorias ul li")))

driver.quit()

with open('buscador_ayudas.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
