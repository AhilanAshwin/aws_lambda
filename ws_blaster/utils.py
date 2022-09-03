import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display


def save_uploadedfile(uploadedfile, file_name, path):
    '''
    Save uploaded file to path directory

    uploadedfile: Uploaded file
    file_name: File name of the uploaded file
    path: Path directory on where to save the file
    '''
    with open(os.path.join(path, file_name), "wb") as f:
        f.write(uploadedfile.getbuffer())


def open_driver(user_path, headless=True):
    '''
    Opens chromedriver and initialize Whatsapp web

    user_path: Path where user credentials are located
    headless: Decides whether to run on headless mode or otherwise

    Returns a chromedriver instance
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(user_path)
    chrome_options.add_argument('--disable-notifications')

    if headless:
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        # Specify user-agent to allow headless mode
        chrome_options.add_argument(
            "user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://web.whatsapp.com/')
    driver.execute_script("window.onbeforeunload = function() {};")
    return driver


def open_driver_blasting(user_path):
    '''
    Opens chromedriver and initialize Whatsapp web

    user_path: Path where user credentials are located
    headless: Decides whether to run on headless mode or otherwise

    Returns a chromedriver instance
    '''
    display = Display(visible=0, size=(1000, 1000))
    display.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(user_path)
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://web.whatsapp.com/')
    driver.execute_script("window.onbeforeunload = function() {};")
    return driver, display

# from selenium.webdriver.common.by import By
# driver, display = open_driver_beta("user-data-dir=Users/AyuhMalaysia/Fizah")
# driver.get_screenshot_as_file("screenshot.png")
# driver.find_element(By.XPATH, "//span[@title='+60 11-6070 0295']").click()
# driver.find_element(By.XPATH, "//div[@class='p3_M1']").click()
# driver.find_element(By.XPATH, "//div[@class='p3_M1']").send_keys("hello")
# driver.find_element(By.XPATH, "//span[@data-testid='send']").click()
