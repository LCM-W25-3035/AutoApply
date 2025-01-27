import asyncio
import json
from Models.analyzer_agent import AnalyzerAgent  # Adjust the import path if needed

# Load the input data from a JSON file
def load_input_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)  # Load and return JSON data
    except Exception as e:
        print(f"Error loading input file: {e}")
        return None

# Run the analyzer agent
async def test_analyzer():
    try:
        # Load the test message from the 'extractor_output.json' file
        input_data = load_input_from_file("extractor_output.json")
        
        if not input_data:
            print("Error: Input data could not be loaded.")
            return

        # Simulate a message for the AnalyzerAgent
        test_message = {"content": input_data}  # Pass the loaded JSON as the content

        # Initialize the AnalyzerAgent
        analyzer_agent = AnalyzerAgent()

        # Run the AnalyzerAgent with the loaded input data
        result = await analyzer_agent.run([test_message])
        
        # Print the result to the console for verification
        print("\n📊 Analyzer Output:")
        print(result)

        # Save the result into a JSON file named 'analyzer_output.json'
        with open("analyzer_output.json", "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
            print("Output saved to 'analyzer_output.json'.")

    except Exception as e:
        print(f"Error occurred: {e}")

# Execute the test function
if __name__ == "__main__":
    asyncio.run(test_analyzer())