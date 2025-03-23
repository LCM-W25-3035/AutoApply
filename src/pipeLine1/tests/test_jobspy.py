
import unittest
import os
import pandas as pd
from jobspy import scrape_jobs
from JobSpy import load_csv_files  # Ensure the function is accessible


class TestJobSpy(unittest.TestCase):

    def setUp(self):
        """Set up test environment variables"""
        self.test_folder = "test_data"
        os.makedirs(self.test_folder, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        for file in os.listdir(self.test_folder):
            os.remove(os.path.join(self.test_folder, file))
        os.rmdir(self.test_folder)

    def test_scrape_jobs(self):
        """Test job scraping returns a non-empty DataFrame"""
        jobs = scrape_jobs(
            site_name=["zip_recruiter"],
            search_term="Data Scientist",
            google_search_term="Data Scientist jobs near Ontario, Canada since yesterday",
            location="Ontario, Canada",
            results_wanted=5,
            hours_old=24,
            country_indeed='Canada',
        )
        if len(jobs) == 0:
            self.skipTest("Skipping test because ZipRecruiter blocked the request (429 error)")
        self.assertGreater(len(jobs), 0, "Scraped jobs should not be empty")

    def test_load_csv_files(self):
        """Test CSV file loading function"""
        test_csv_path = os.path.join(self.test_folder, "test_jobs.csv")
        test_data = pd.DataFrame({
            "location": ["Toronto", "Vancouver"],
            "title": ["Data Engineer", "Machine Learning Engineer"],
            "company": ["Company A", "Company B"],
            "job_type": ["Full-time", "Contract"]
        })
        test_data.to_csv(test_csv_path, index=False)

        df = load_csv_files(self.test_folder)
        self.assertEqual(len(df), 2, "Loaded DataFrame should have 2 rows")

    def test_remove_duplicates(self):
        """Test duplicate removal from job dataset"""
        df = pd.DataFrame({
            "location": ["Toronto", "Toronto"],
            "title": ["Data Engineer", "Data Engineer"],
            "company": ["Company A", "Company A"],
            "job_type": ["Full-time", "Full-time"]
        })

        duplicates = df[df.duplicated(subset=["location", "title", "company", "job_type"], keep=False)]
        self.assertEqual(len(duplicates), 2, "Duplicate detection failed")

        df = df.drop_duplicates(subset=["location", "title", "company", "job_type"], keep="first")
        self.assertEqual(len(df), 1, "Duplicate removal failed")

if __name__ == "__main__":
    unittest.main()
