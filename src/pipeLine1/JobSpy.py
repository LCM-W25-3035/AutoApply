# %%
import csv
from jobspy import scrape_jobs

search_keywords = ['it','data analysis','business analytics','data engineer','machine learning engineer','LLM Enginner','data scientist']
search_locations = ['Ontario, Canada','Alberta, Canada', 'British Columbia, Canada', 'Quebec, Canada']
#search_keywords = ['data engineer']
#search_locations = ['Ontario, Canada']

for search_keyword in search_keywords:
    for search_location in search_locations:
        print(search_keyword)
        print(search_location)
        jobs = scrape_jobs(
            #site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"]
            site_name=["zip_recruiter", "google"],
            search_term=search_keyword,
            google_search_term= search_keyword + " jobs near " + search_location + " since yesterday",
            location= search_location,
            results_wanted=20000,
            hours_old=24,
            country_indeed='Canada',
            
            #linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
            # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
        )
        jobs['Provincia']=search_location.split(',')[0]
        jobs['Keyword']=search_keyword
        print(f"Found {len(jobs)} jobs")
        print(jobs.head())
        jobs.to_csv(search_keyword + "_" + search_location +".csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel

# %%
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # Disable SettingWithCopyWarning

def load_csv_files(folder_path):
    df_list = []
    
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            if os.path.getsize(file_path) > 0:  # Check if the file is non-empty
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:  # Ensure the file has actual data
                        df_list.append(df)
                except pd.errors.EmptyDataError:
                    print(f"Skipping empty file: {file}")
                except pd.errors.ParserError:
                    print(f"Skipping corrupt file: {file}")
    
    # Concatenate all DataFrames into a single one
    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

# Example usage
folder_path = r"C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\JobSpy"
dataframe = load_csv_files(folder_path)

print(dataframe.head())  # Print only if the dataframe is not empty


# %%
len(dataframe)

# %%
# Check for duplicate rows based on specific columns
criteria_columns = ["location", "title","company","job_type"]  # Change to your criteria columns
#criteria_columns = ["URL"]  # Change to your criteria columns
duplicates = dataframe[dataframe.duplicated(subset=criteria_columns, keep=False)]
print("Duplicate rows based on criteria:")
print(duplicates)
#duplicates.to_csv('duplicates.csv')

# %%
# Remove duplicate rows
dataframe = dataframe.drop_duplicates(subset=criteria_columns, keep='first')
print("Dataframe after removing duplicates:")
print(dataframe)

# %%
len(dataframe)

# %%


#JobSpy_scraped_jobs.csv

new_dataframe = dataframe[['title','company','location','salary_source','date_posted','description','job_url','Provincia','Keyword']]
new_dataframe.rename(columns={'title': 'Job Title', 'company': 'Company Name','location':'Location','salary_source':'Salary','date_posted':'Posted Day','description':'Job Description','job_url':'job url'}, inplace=True)

new_dataframe.head(5)

new_dataframe.to_csv('JobSpy_scraped_jobs.csv',index=False)
#Job Title	Company Name	Location	Salary	Posted Day	Job Description	job url	Provincia	Keyword



