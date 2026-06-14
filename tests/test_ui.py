import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.environ.get("BASE_URL", "http://98.82.242.170:32500")


@pytest.fixture(scope="module")
def driver():
    """Set up headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_frontend_sentiment(driver):
    """
    Headless Selenium test:
    - Open the frontend
    - Send a test sentence to text-input
    - Click submit-btn
    - Assert result-output is non-empty and contains POSITIVE, NEGATIVE, or Confidence
    """
    driver.get(f"{BASE_URL}/")

    text_input = driver.find_element(By.ID, "text-input")
    submit_btn = driver.find_element(By.ID, "submit-btn")

    test_sentence = "The food was absolutely delicious and the chef clearly has exceptional skill"
    text_input.clear()
    text_input.send_keys(test_sentence)

    submit_btn.click()

    wait = WebDriverWait(driver, 15)
    result_output = wait.until(
        EC.presence_of_element_located((By.ID, "result-output"))
    )

    wait.until(lambda d: d.find_element(By.ID, "result-output").text.strip() != "")

    result_text = result_output.text.strip()

    assert result_text != "", "result-output is empty after clicking submit"

    assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"]), \
        f"result-output does not contain expected keywords. Got: '{result_text}'"