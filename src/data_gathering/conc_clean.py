"""Chat GPT o1"""
"""Write a Python script that reads lists of keywords and provinces from two text files, keywords.txt 
and providence.txt, respectively, then iterates over all CSV files named using each combination of 
keyword and province (e.g., glassdoor_jobs_{keyword}{province}.csv), combines them into a single pandas 
DataFrame, cleans the data by dropping empty columns and duplicates, standardizing column names, and 
trimming whitespace, and finally saves the consolidated, cleaned result to src\data_gathering\Jobs-Data_Cleaned.csv. 
This script should log its activity (informational messages, errors, and warnings) with the logging module, 
handle missing files gracefully, and exit if no valid data is found."""

import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_data(df):
    """Performs data cleaning."""
    # Drop empty columns
    df.dropna(axis=1, how='all', inplace=True)

    # Drop duplicate rows
    df.drop_duplicates(inplace=True)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    blank_rows = df.isna().all(axis=1) | df.eq("").all(axis=1)
    df = df[~blank_rows]

    # Remove leading/trailing whitespace in string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

    return df

def main():
    try:
        df1=pd.read_csv("Jobs-Data_Scraped.csv")
        df2=pd.read_csv("src/data_gathering/JobSpy_Octoparse_combined_jobs.csv")
        df3=pd.read_csv('src/data_gathering//JobSpy_scraped_jobs.csv')
    except FileNotFoundError:
        logging.error("One or more required files are missing.")
        return

    data= pd.concat([df1, df2,df3], ignore_index=True)

    logging.info("Cleaning data...")
    cleaned_data = clean_data(data)

    output_file = "src\data_gathering\Jobs-Data_Cleaned.csv"
    cleaned_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    logging.info(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    main()
