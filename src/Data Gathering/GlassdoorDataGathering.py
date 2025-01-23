from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random


load_dotenv()
GLASSDOOR_EMAIL = os.getenv('GLASSDOOR_EMAIL')
GLASSDOOR_PASSWORD = os.getenv('GLASSDOOR_PASSWORD')

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

def dismiss_popup(driver):
    """Dismiss all modals dynamically if found and restore scrolling."""
    try:
        # Verificar si el modal existe
        modal_exists = driver.execute_script("""
            return document.querySelector("div[class*='modal']") !== null;
        """)

        if modal_exists:
            # Si existe, eliminar el modal y restaurar el scroll
            driver.execute_script("""
                var modal = document.querySelector("div[class*='modal']");
                if (modal) modal.remove();

                // Restaurar el scroll en body y html
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
            """)
            print("Popup removed with JavaScript.")
            job_details_container = driver.find_element(By.CLASS_NAME, 'TwoColumnLayout_jobDetailsContainer__qyvJZ')
            driver.execute_script("arguments[0].scrollIntoView(true);", job_details_container)
            print("Right column scrolled into view.")
        else:
            print("No popup found to remove.")

    except Exception as e:
        print(f"Error while checking or removing popup: {e}")


def search_jobs(driver, job_title, location):
    """Searches for jobs based on job title and location."""
    try:
        # Wait for and fill in the job title input field
        job_title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchBar-jobTitle'))
        )
        job_title_input.clear()
        job_title_input.send_keys(Keys.CONTROL + 'a')  # Select all text
        job_title_input.send_keys(Keys.BACKSPACE) 
        job_title_input.send_keys(job_title)
        human_delay(1, 3)

        # Wait for and fill in the location input field
        location_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchBar-location'))
        )
        location_input.clear()
        location_input.send_keys(Keys.CONTROL + 'a')  # Select all text
        location_input.send_keys(Keys.BACKSPACE) 
        location_input.send_keys(location)
        human_delay(1, 3)
        # After typing the location, give it some time for the automatic search to trigger

         # Trigger input and change events for location
        driver.execute_script("""
            var input = arguments[0];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, location_input)

        human_delay(2, 4)
        location_input.send_keys(Keys.ENTER)
        # Attempt to handle location suggestions
        try:
            location_suggestions = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.autocomplete_suggestionsList__Wg2ty li'))
            )
            for suggestion in location_suggestions:
                if suggestion.text.strip().lower() == location.lower():
                    suggestion.click()
                    print(f"Location suggestion selected: {location}")
                    break
        except Exception:
            print("No location suggestions displayed. Proceeding without selection.")

        # Simulate a short delay and dismiss any popup
        human_delay(2, 4)
        dismiss_popup(driver)

        print(f"Search completed for job title: {job_title} and location: {location}")

    except Exception as e:
        print(f"Error during job search: {e}")


def scrape_job_listings(driver, keyword):
    """Scrapes job listings from the search results."""
    jobs_data = []  #Container Job Offer
    processed_jobs = set() #Unique Job offer

    while True:
        new_jobs_found = False
        try:
            # Wait until every job card is loaded 
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobCard'))
            )
            print("Job cards loaded successfully.")
            human_delay(2, 3)

            # Get all job card 
            job_cards = driver.find_elements(By.CLASS_NAME, 'jobCard')

            for job_card in job_cards:
                try:
                    job_titlee = job_card.text.strip()  # Get job title unique
                    if job_titlee in processed_jobs:
                        continue  # if processed pass next job card

                    new_jobs_found = True  # Indicar que hay una nueva tarjeta
                    processed_jobs.add(job_titlee)  

                    # Click en la tarjeta para cargar la descripción
                    job_card.click()
                    dismiss_popup(driver)
                    human_delay(2, 3)

                    # Extraer información visible directamente de la tarjeta
                    job_title_element = job_card.find_element(By.CLASS_NAME, 'JobCard_jobTitle__GLyJ1')
                    job_title = job_title_element.text.strip()
                    company_name = job_card.find_element(By.CLASS_NAME, 'EmployerProfile_compactEmployerName__9MGcV').text.strip()
                    location = job_card.find_element(By.CLASS_NAME, 'JobCard_location__Ds1fM').text.strip()
                    job_url = job_title_element.get_attribute('href')

                    # Manejar información opcional
                    try:
                        salary = job_card.find_element(By.CLASS_NAME, 'JobCard_salaryEstimate__QpbTW').text.strip()
                    except Exception:
                        salary = "N/A"

                    try:
                        posted_day = job_card.find_element(By.CLASS_NAME, 'JobCard_listingAge__jJsuc').text.strip()
                    except Exception:
                        posted_day = "N/A"

                    # Extraer la descripción del trabajo
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    try:
                        #job_description = driver.find_element(By.CLASS_NAME, 'JobDetails_jobDescription__uW_fK').text.strip()
                        job_description = soup.find('div', class_='JobDetails_jobDescription__uW_fK').text.strip()
                    except Exception:
                        job_description = "N/A"

                    # Añadir toda la información al diccionario
                    jobs_data.append({
                        'Job Title': job_title,
                        'Company Name': company_name,
                        'Location': location,
                        'Salary': salary,
                        'Posted Day': posted_day,
                        'Job Description': job_description,
                        'job url': job_url if job_url else "N/A"
                    })


                except Exception as job_error:
                    print(f"Error processing job card: {job_error}")
                    continue

                # Save the data as backup
                jobs_df = pd.DataFrame(jobs_data)
                jobs_df.drop_duplicates(inplace=True)
                jobs_df.to_csv(f'glassdoor_jobs_backup{keyword}.csv', index=False, encoding='utf-8-sig')

                print("Data saved to 'glassdoor_jobs_backup.csv'.")

            if not new_jobs_found:
                print("No new job cards found. Exiting loop.")
                break
            try:
                show_more_button = WebDriverWait(driver, 20).until(
                     EC.element_to_be_clickable((By.XPATH, '//button[@data-test="load-more"]'))
                 )
                show_more_button.click()
                print("Clicked 'Show more jobs' button. Loading more jobs...")
                human_delay(3, 4)

            except Exception:
                 print("No more 'Show more jobs' button or error occurred.")
                 break
                
        except Exception as e:
            print("Error occurred while loading jobs:", e)
            break

    # Saved Data Into a CSV file
    df = pd.DataFrame(jobs_data)
    df.drop_duplicates(inplace=True)
    df.to_csv(f"glassdoor_jobs_{keyword}.csv", index=False, encoding='utf-8-sig')
    print(f'Scraping complete. Data saved to f"glassdoor_jobs_{keyword}.csv".')



if __name__ == "__main__":
    start_time = time.time()
    # Set up Selenium WebDriver
    options = Options()
    options.headless = False  # Set to True for headless mode
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    keys =[]
    with open("keywords.txt", 'r') as file:
        for line in file:
            keys.append(line.strip())
        print(line.strip())

    print(keys)
    # Maximize browser windows
    driver.maximize_window()

    try:
        login_to_glassdoor(driver, GLASSDOOR_EMAIL, GLASSDOOR_PASSWORD)
        navigate_to_jobs(driver)
        for i in keys:
            search_jobs(driver, i, "Canada")
            scrape_job_listings(driver, i)
        
        #concating each csv file
        data_final = pd.DataFrame()
        for documento in keys: 
            data1 = pd.read_csv(f"glassdoor_jobs_{documento}.csv")
            data_final = pd.concat([data_final, data1], ignore_index=True)

        print(data_final.shape)

        data_final = data_final[~data_final.duplicated(keep='first')]
        data_final.shape

        data_final.to_csv("Jobs-Data_Scraped.csv", index=False)


    
    finally:
        time.sleep(5)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total execution time: {elapsed_time:.2f} Seconds")
        driver.quit()
