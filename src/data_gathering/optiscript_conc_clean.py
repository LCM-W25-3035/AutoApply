import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_list_from_file(filename):
    """Reads a list of items from a given file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return []
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
        return []

def load_and_combine_data(keywords, provinces):
    """Loads and combines job data from diverse files into a single DataFrame."""
    data_final = pd.DataFrame()
    
    for keyword in keywords:
        for province in provinces:
            file_path = f"src\data_gathering\glassdoor_jobs_{keyword}{province}.csv"
            if os.path.exists(file_path):
                try:
                    data = pd.read_csv(file_path)
                    data['Provincia'] = province
                    data['Keyword'] = keyword
                    data_final = pd.concat([data_final, data], ignore_index=True)
                except Exception as e:
                    logging.error(f"Error reading {file_path}: {e}")
    
    data_final.drop_duplicates(keep='first', inplace=True)
    return data_final

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
    """Main function that executes the process."""
    logging.info("Starting data processing...")

    keywords = read_list_from_file("keywords.txt")
    provinces = read_list_from_file("providence.txt")

    if not keywords or not provinces:
        logging.error("No keywords or provinces found. Exiting process.")
        return

    data = load_and_combine_data(keywords, provinces)

    if data.empty:
        logging.warning("No data was loaded. Exiting process.")
        return

    logging.info("Cleaning data...")
    cleaned_data = clean_data(data)

    output_file = "src\data_gathering\Jobs-Data_Cleaned.csv"
    cleaned_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    logging.info(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    main()
