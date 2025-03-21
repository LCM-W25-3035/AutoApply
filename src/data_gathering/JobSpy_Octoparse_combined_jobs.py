# %%
import os
import pandas as pd

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
    merged_df = df1.merge(df2, on=criteria_columns, how='left', indicator=True)
    unique_records = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    #unique_records = unique_records.dropna(axis=1) #dropna inconsistent output. do not use
    return unique_records.iloc[:, 0:9]


df1 = dataframe  # First DataFrame
df1.drop(['Country', 'Job_Type', 'Benifits', 'Job_rating', 'Email'],axis=1,inplace=True)
df1['Description'] = df1['Description'].fillna("N/A")
df1['Salary'] = df1['Salary'].fillna("0")


df3 = df1.iloc[:, 0:8]

#Job Title	Company Name	Location	Salary	Posted Day	Job Description	job url	Provincia	Keyword
df4 = df3[['Title','Posted_By','Search_Location','Salary','Description','URL','Search_Keyword']]
df4.rename(columns={'Title': 'Job Title', 'Posted_By': 'Company Name','Search_Location':'Location','Description':'Job Description','URL':'job url','Search_Keyword':'Keyword'}, inplace=True)
df4.insert(4, 'Posted Day','')
df4.insert(7, 'Provincia',df4['Location'])

df5=pd.read_csv(r'C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\JobSpy\JobSpy_scraped_jobs.csv')

df4 = pd.concat([df4, df5], ignore_index=True)


df2 = pd.read_csv(r'C:\CAROL\Personal\Canada\Lambton\3rd Term\2025W-T3 BDM 3035 - Big Data Capstone Project 01 (DSMM Group 1)\Oscar\Jobs-Data_Scraped.csv')


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


