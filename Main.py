from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "appointment")))
        print("Login successful")

    except Exception as e:
        print(f"Error during login: {e}")
        driver.save_screenshot("login_error.png")

# Function to check for new appointments
def check_appointments(driver):
    try:
        appointment_text = driver.find_element(By.ID, "appointment").text
        return "No appointments available" not in appointment_text
    except Exception as e:
        print(f"Error during checking appointments: {e}")
        return False

# Function to book an appointment
def book_appointment(driver):
    try:
        book_button = driver.find_element(By.ID, "book_appointment_button")
        book_button.click()
        print("Appointment booked successfully!")
    except Exception as e:
        print(f"Error during booking appointment: {e}")

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
        time.sleep(60)

driver.quit()
