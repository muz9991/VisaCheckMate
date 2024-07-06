from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Setup WebDriver
driver = webdriver.Chrome()  # Ensure the ChromeDriver path is set if needed

# Function to login
def login(driver, username, password):
    driver.get("https://visas-de.tlscontact.com/appointment/gb/gbMNC2de/2521249")
    try:
        # Wait for and fill the login form
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        login_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        print("Entering username")
        login_field.send_keys(username)
        
        print("Entering password")
        password_field.send_keys(password)
        
        print("Submitting login form")
        password_field.send_keys(Keys.RETURN)
        
        # Handle the redirect and wait for the next page to load
        WebDriverWait(driver, 20).until(EC.url_contains("https://visas-de.tlscontact.com/"))
        
        # Optionally, you can add a specific check for a successful login, such as checking for a specific element
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tls-appointment-time-picker")))
        print("Login successful")

    except Exception as e:
        print(f"Error during login: {e}")
        driver.save_screenshot("login_error.png")

# Function to check for new appointments
def check_appointments(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tls-appointment-time-picker")))
        slots = driver.find_elements(By.CSS_SELECTOR, ".tls-time-unit:not(.-unavailable)")
        return len(slots) > 0
    except Exception as e:
        print(f"Error during checking appointments: {e}")
        return False

# Function to book an appointment
def book_appointment(driver):
    try:
        available_slots = driver.find_elements(By.CSS_SELECTOR, ".tls-time-unit:not(.-unavailable)")
        if available_slots:
            slot = available_slots[0]
            slot_date = slot.find_element(By.XPATH, "../../div[@class='tls-time-group--header-title']").text
            slot_time = slot.text
            slot.click()  # Book the first available slot
            print("Appointment booked successfully!")
            send_webhook_notification("Appointment booked successfully!", slot_date, slot_time, driver.current_url)
        else:
            print("No available slots found.")
            send_webhook_notification("No appointments available", None, None, driver.current_url)
    except Exception as e:
        print(f"Error during booking appointment: {e}")

# Function to send a webhook notification
def send_webhook_notification(message, date, time, url):
    webhook_url = "https://hook.eu2.make.com/t4l44z3dvaxp7on5ka5yhhl5ekrt5xj7"  # Webhook URL
    payload = {
        'text': f"{message}\nDate: {date if date else 'N/A'}\nTime: {time if time else 'N/A'}\nURL: {url}"
    }
    print(f"Sending webhook with payload: {payload}")
    try:
        response = requests.post(webhook_url, json=payload)
        print(f"Webhook response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            print("Webhook sent successfully.")
        else:
            print(f"Failed to send webhook. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending webhook: {e}")

# Main script
username = "Waleedbaloch343@gmail.com"
password = "Mehboob@180"

login(driver, username, password)

while True:
    if check_appointments(driver):
        book_appointment(driver)
        break
    else:
        print("No appointments available, checking again in 60 seconds...")
        send_webhook_notification("No appointments available", None, None, driver.current_url)
        time.sleep(3600)

driver.quit()
