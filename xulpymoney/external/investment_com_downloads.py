from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

driver = webdriver.Firefox(executable_path="./geckodriver")
driver.get('https://es.investing.com/')
print(dir(driver))
print(dir(driver.switch_to))
sleep(20)
f=open("prueba.html","w")
f.write(driver.page_source)
f.close()
#for i, div in enumerate(driver.find_elements_by_tag_name("div")):
#    print (i, div, div.id, dir(div))
for elemente in driver.find_elements_by_class_name("truste_overlay"):
    print(elemente, elemente.text, dir(elemente))
    elemente.screenshot("prueba.png")
    for ano in elemente.anonymous_children:
         print (ano)
#    try:
#        driver.switch_to.frame(i)
#        print(iframe, iframe.size)
#    except:
#        print(i, iframe.page_source, "no pudo")
#        continue
#    print( iframe, dir(iframe),iframe.id, iframe.size)
#    dataElement = browser.find_element_by_css_selector('a.call')
#    print(dataElement)#driver.switch_to.frame('trustee_box_overlay')
    #except:
        #print("Mal", i)


#wait = WebDriverWait(driver, 30)
#element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.call')))
#print(element)

driver.quit()