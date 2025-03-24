# %%
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # Disable SettingWithCopyWarning

def load_csv_files(folder_path):
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    df_list = []
    
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        df_list.append(df)
    
    # Concatenate all DataFrames into a single one
    final_df = pd.concat(df_list, ignore_index=True)
    return final_df

# Example usage
folder_path = r"C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\Octoparse\To be combined\Combined"  # Change this to your folder path
dataframe = load_csv_files(folder_path)
print(dataframe.head())


# %%
dataframe

# %%
len(dataframe)

# %%
# Check for duplicate rows based on specific columns
criteria_columns = ["Search_Location", "Title","Posted_By","Job_Type"]  # Change to your criteria columns
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
dataframe.columns

# %%
# Compare data from two different DataFrames and display unique records from the first DataFrame
def find_unique_records(df1, df2, criteria_columns):
    # Standardizing column names for merging
    df1 = df1.rename(columns={
        'Title': 'Job Title',
        'Posted_By': 'Company Name',
        'Search_Location': 'Provincia'
    })
    
    # Normalize text formatting to avoid mismatches
    for col in criteria_columns:
        df1[col] = df1[col].str.strip().str.lower()
        df2[col] = df2[col].str.strip().str.lower()

    print("\n=== Checking Merging Process ===")
    print("df1 sample:\n", df1[criteria_columns].head())
    print("df2 sample:\n", df2[criteria_columns].head())

    merged_df = df1.merge(df2, on=criteria_columns, how='left', indicator=True)
    
    # Print how many records matched
    print("\n=== Merge Results ===")
    print(merged_df['_merge'].value_counts())  # Counts of left_only, right_only, both

    unique_records = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    print("\n=== Unique Records Found ===")
    print(unique_records)

    return unique_records





df1 = dataframe  # First DataFrame
df1.drop(['Country', 'Job_Type', 'Benifits', 'Job_rating', 'Email'],axis=1,inplace=True)
df1['Description'] = df1['Description'].fillna("N/A")
df1['Salary'] = df1['Salary'].fillna("0")


df3 = df1.iloc[:, 0:8] #selecting all rows and columns from index 0 to 7

#Job Title	Company Name	Location	Salary	Posted Day	Job Description	job url	Provincia	Keyword
#Conform df4 to column names of jobs scraped from jobspy (zip_recruiter, google)
df4 = df3[['Title','Posted_By','Search_Location','Salary','Description','URL','Search_Keyword']]
df4.rename(columns={'Title': 'Job Title', 'Posted_By': 'Company Name','Search_Location':'Location','Description':'Job Description','URL':'job url','Search_Keyword':'Keyword'}, inplace=True)
df4.insert(4, 'Posted Day','')
df4.insert(7, 'Provincia',df4['Location'])

#jobs scraped via jobspy
df5=pd.read_csv(r'C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\JobSpy\JobSpy_scraped_jobs.csv')

#combine Octoparse and Jobspy job dataset
df4 = pd.concat([df4, df5], ignore_index=True)


#jobs from Oscar scraped from Glassdoor
df2 = pd.read_csv(r'C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\Oscar\Jobs-Data_Scraped.csv')

#get unique records from Octoparse (Indeed), Jobspy (Zip Recruiter and Google) and Oscar(Glassdoor)
criteria_columns = ['Job Title','Company Name','Provincia'] 
unique_records = find_unique_records(df4, df2, criteria_columns)
print("Unique records from first DataFrame:")
print(unique_records)
len(unique_records)


# %%
unique_records.head(5)

# %%
unique_records.rename(columns={'Location_x': 'Location', 'Salary_x': 'Salary','Posted Day_x':'Posted Day','Job Description_x':'Job Description','job url_x':'job url','Keyword_x':'Keyword'}, inplace=True)

# %%
unique_records.to_csv('JobSpy_Octoparse_combined_jobs.csv',index=False)


# %% [markdown]
# 


