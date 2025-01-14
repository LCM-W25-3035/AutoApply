import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os

GLASSDOOR_EMAIL = 'oscar_quintero_26@hotmail.com'
password = os.environ.get('GLASSDOOR_PASSWORD') 
GLASSDOOR_PASSWORD = f"{password}"


def human_delay(min_seconds, max_seconds):
    """Adds a random delay to simulate human-like browsing behavior."""
    delay_time = random.uniform(min_seconds, max_seconds)
    time.sleep(delay_time)

def login_to_glassdoor(driver, email, password):
    """Logs into Glassdoor using the provided credentials."""
    login_url = 'https://www.glassdoor.ca/profile/login_input.htm'
    driver.get(login_url)
    human_delay(1, 3)

    try:
        # Wait for and enter email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'inlineUserEmail'))
        )
        email_field.send_keys(email)
        print("Email entered.")
        human_delay(1, 2)

        # Wait for and click the 'Continue' button
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
        )
        continue_button.click()
        print("Clicked continue button.")
        human_delay(1, 2)

        # Wait for and enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'inlineUserPassword'))
        )
        password_field.send_keys(password)
        print("Password entered.")
        human_delay(1, 2)

        # Wait for and click the 'Login' button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
        )
        login_button.click()
        print("Logged in successfully.")
        human_delay(3, 5)

        # Wait for redirection after login
        WebDriverWait(driver, 30).until(EC.url_contains('glassdoor.ca'))
        print("Redirection successful.")

    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        exit()

def navigate_to_jobs(driver):
    """Navigates to the 'Jobs' section on Glassdoor."""
    try:
        # Wait and click the 'Jobs' button
        jobs_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="site-header-jobs"] > a'))
        )
        jobs_button.click()
        print("Clicked 'Jobs' button.")
        human_delay(2, 4)

        # Wait for Jobs page to load
        WebDriverWait(driver, 10).until(EC.url_contains('/Job/index.htm'))
        print("Navigated to Jobs page.")

    except Exception as e:
        print("Error during navigation to Jobs:", e)
        driver.quit()
        exit()

def search_jobs(driver, job_title, location):
    """Searches for jobs based on job title and location."""
    try:
        # Wait for and fill in the job title input field
        job_title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchBar-jobTitle'))
        )
        job_title_input.clear()
        job_title_input.send_keys(job_title)
        human_delay(1, 3)

        # Wait for and fill in the location input field
        location_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchBar-location'))
        )
        location_input.clear()
        location_input.send_keys(location)
        human_delay(1, 3)
        # After typing the location, give it some time for the automatic search to trigger
        human_delay(2, 4)  # Simulating a short delay after typing
        # Optionally, if necessary, wait for results to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'autocomplete_suggestionsList__Wg2ty')))
        print("Search results loaded.")

        location_suggestions = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.autocomplete_suggestionsList__Wg2ty li'))
        )

        for suggestion in location_suggestions:
            if suggestion.text.strip().lower() == location.lower():
                suggestion.click()  # Click the matching suggestion
                print(f"Location selected: {location}")
                break

    except Exception as e:
        print("Error during job search:", e)
        driver.quit()
        exit()

def scrape_job_listings(driver):
    """Scrapes job listings from the search results."""
    jobs_data = []
    while True:
        try:
            # Wait for job cards to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobCard'))
            )
            print("Job cards loaded successfully.")
            human_delay(2, 4)

            # Parse the HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract job cards
            job_cards = soup.find_all('div', class_=lambda x: x and 'jobCard' in x)
            for job_card in job_cards:

                job_title = job_card.find('a', class_=lambda x: x and 'jobTitle' in x)
                company_name = job_card.find('span', class_='EmployerProfile_compactEmployerName__9MGcV')
                location = job_card.find('div', class_=lambda x: x and 'location' in x)
                salary = job_card.find('div', class_=lambda x: x and 'salary' in x)
                job_url = job_title['href'] if job_title else None

                try:
                    job_description_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'JobDetails_jobDescription__uW_fK'))
                    )
                    job_description = job_description_element.text
                except:
                    job_description = 'N/A'
                    
                jobs_data.append({
                    'Job Title': job_title.text.strip() if job_title else 'N/A',
                    'Company Name': company_name.text.strip() if company_name else 'N/A',
                    'Job Descriptions': job_description.strip() if job_description else 'N/A',
                    'Location': location.text.strip() if location else 'N/A',
                    'Salary': salary.text.strip() if salary else 'N/A',
                    'Job URL': f"{job_url}" if job_url else None,
                })

            # Find and click the "Show more jobs" button
            try:
                show_more_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-test="load-more"]'))
                )
                show_more_button.click()
                print("Clicked 'Show more jobs' button. Loading more jobs...")
                human_delay(3, 5)

            except Exception:
                print("No more 'Show more jobs' button or error occurred.")
                break

        except Exception as e:
            print("Error occurred while loading jobs:", e)
            break

    jobs_df = pd.DataFrame(jobs_data)
    jobs_df.drop_duplicates(inplace=True)
    jobs_df.to_csv('glassdoor_jobs.csv', index=False)


if __name__ == "__main__":
    # Set up Selenium WebDriver
    options = Options()
    options.headless = False  # Set to True for headless mode
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Maximize browser window
    driver.maximize_window()

    try:
        login_to_glassdoor(driver, GLASSDOOR_EMAIL, GLASSDOOR_PASSWORD)
        navigate_to_jobs(driver)
        search_jobs(driver, "IT", "Ontario, Canada")
        scrape_job_listings(driver)

    finally:
        time.sleep(5)
        driver.quit()
