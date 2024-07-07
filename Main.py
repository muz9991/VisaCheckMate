from threading import Thread
import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# Setup WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

chrome_service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Logs and status
logs = []
status = {
    "next_check": None,
    "last_check": None,
    "appointment_booked": False,
    "appointment_date": None,
    "appointment_time": None,
    "current_url": None
}

def login(driver, username, password):
    driver.get("https://visas-de.tlscontact.com/appointment/gb/gbMNC2de/2521249")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        login_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        logs.append("Entering username")
        print("Entering username")
        login_field.send_keys(username)
        
        logs.append("Entering password")
        print("Entering password")
        password_field.send_keys(password)
        
        logs.append("Submitting login form")
        print("Submitting login form")
        password_field.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 20).until(EC.url_contains("https://visas-de.tlscontact.com/"))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tls-appointment-time-picker")))
        logs.append("Login successful")
        print("Login successful")

    except Exception as e:
        logs.append(f"Error during login: {e}")
        print(f"Error during login: {e}")
        driver.save_screenshot("login_error.png")

def check_appointments(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tls-appointment-time-picker")))
        slots = driver.find_elements(By.CSS_SELECTOR, ".tls-time-unit:not(.-unavailable)")
        return len(slots) > 0
    except Exception as e:
        logs.append(f"Error during checking appointments: {e}")
        print(f"Error during checking appointments: {e}")
        return False

def book_appointment(driver):
    try:
        available_slots = driver.find_elements(By.CSS_SELECTOR, ".tls-time-unit:not(.-unavailable)")
        if available_slots:
            slot = available_slots[0]
            slot_date = slot.find_element(By.XPATH, "../../div[@class='tls-time-group--header-title']").text
            slot_time = slot.text
            slot.click()  # Book the first available slot
            logs.append("Appointment booked successfully!")
            print("Appointment booked successfully!")
            send_webhook_notification("Appointment booked successfully!", slot_date, slot_time, driver.current_url)
            status.update({
                "appointment_booked": True,
                "appointment_date": slot_date,
                "appointment_time": slot_time
            })
        else:
            logs.append("No available slots found.")
            print("No available slots found.")
            send_webhook_notification("No appointments available", None, None, driver.current_url)
    except Exception as e:
        logs.append(f"Error during booking appointment: {e}")
        print(f"Error during booking appointment: {e}")

def send_webhook_notification(message, date, time, url):
    webhook_url = "https://hook.eu2.make.com/t4l44z3dvaxp7on5ka5yhhl5ekrt5xj7"
    payload = {
        'text': f"{message}\nDate: {date if date else 'N/A'}\nTime: {time if time else 'N/A'}\nURL: {url}"
    }
    logs.append(f"Sending webhook with payload: {payload}")
    print(f"Sending webhook with payload: {payload}")
    try:
        response = requests.post(webhook_url, json=payload)
        logs.append(f"Webhook response: {response.status_code} - {response.text}")
        print(f"Webhook response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            logs.append("Webhook sent successfully.")
            print("Webhook sent successfully.")
        else:
            logs.append(f"Failed to send webhook. Status code: {response.status_code}")
            print(f"Failed to send webhook. Status code: {response.status_code}")
    except Exception as e:
        logs.append(f"Error sending webhook: {e}")
        print(f"Error sending webhook: {e}")

def main_task():
    login(driver, username, password)

    while True:
        status['last_check'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        print(f"Last check: {status['last_check']}")
        if check_appointments(driver):
            book_appointment(driver)
            break
        else:
            logs.append("No appointments available, checking again in 1 hour...")
            print("No appointments available, checking again in 1 hour...")
            send_webhook_notification("No appointments available", None, None, driver.current_url)
            status['next_check'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 3600))
            print(f"Next check: {status['next_check']}")
            time.sleep(3600)

    driver.quit()

if __name__ == "__main__":
    main_task()
