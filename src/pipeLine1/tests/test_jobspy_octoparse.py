import unittest
import os
import pandas as pd
from JobSpy_Octoparse_combined_jobs import load_csv_files, find_unique_records

class TestJobSpyOctoparse(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        self.test_folder = "test_data"
        os.makedirs(self.test_folder, exist_ok=True)

        # Create test CSV files
        test_data_1 = pd.DataFrame({
            "Search_Location": ["Toronto", "Vancouver"],
            "Title": ["Data Engineer", "Machine Learning Engineer"],
            "Posted_By": ["Company A", "Company B"],
            "Job_Type": ["Full-time", "Contract"],
            "URL": ["https://job1.com", "https://job2.com"]
        })
        test_data_1.to_csv(os.path.join(self.test_folder, "test_jobs1.csv"), index=False)

        test_data_2 = pd.DataFrame({
            "Search_Location": ["Toronto", "Ottawa"],
            "Title": ["Data Engineer", "Software Developer"],
            "Posted_By": ["Company A", "Company C"],
            "Job_Type": ["Full-time", "Part-time"],
            "URL": ["https://job1.com", "https://job3.com"]
        })
        test_data_2.to_csv(os.path.join(self.test_folder, "test_jobs2.csv"), index=False)

    def tearDown(self):
        """Clean up test files"""
        for file in os.listdir(self.test_folder):
            os.remove(os.path.join(self.test_folder, file))
        os.rmdir(self.test_folder)

    def test_load_csv_files(self):
        """Test CSV file loading function"""
        df = load_csv_files(self.test_folder)
        self.assertEqual(len(df), 4, "Loaded DataFrame should have 4 rows")

    def test_remove_duplicates(self):
        """Test duplicate job removal"""
        df = load_csv_files(self.test_folder)
        criteria_columns = ["Search_Location", "Title", "Posted_By", "Job_Type"]

        duplicates = df[df.duplicated(subset=criteria_columns, keep=False)]
        self.assertEqual(len(duplicates), 2, "Duplicate detection failed")

        df = df.drop_duplicates(subset=criteria_columns, keep="first")
        self.assertEqual(len(df), 3, "Duplicate removal failed")

    def test_find_unique_records(self):
        """Test finding unique records between two datasets"""
        df1 = load_csv_files(self.test_folder)
        df2 = pd.DataFrame({"Title": ["Data Engineer", "Software Developer"],  
        "Posted_By": ["Company A", "Company C"],  
        "Search_Location": ["Toronto", "Ottawa"]  
})

        # Rename columns to match `find_unique_records`
        df2.rename(columns={'Title': 'Job Title', 'Posted_By': 'Company Name', 'Search_Location': 'Provincia'}, inplace=True)


        criteria_columns = ["Job Title", "Company Name", "Provincia"]
        unique_records = find_unique_records(df1, df2, criteria_columns)
        self.assertEqual(len(unique_records), 1, "Unique records extraction failed")

if __name__ == "__main__":
    unittest.main()
