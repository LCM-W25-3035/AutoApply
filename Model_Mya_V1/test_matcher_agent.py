import asyncio
import json
from matcher_agent import MatcherAgent  # Adjust path if needed

# Load the input data from a JSON file (e.g., 'analyzer_output.json')
def load_input_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)  # Load and return JSON data
    except Exception as e:
        print(f"Error loading input file: {e}")
        return None

# Run the matcher agent
async def test_matcher():
    try:
        # Load the test message from the 'analyzer_output.json' file
        input_data = load_input_from_file("analyzer_output.json")
        
        if not input_data:
            print("Error: Input data could not be loaded.")
            return

        # Simulate a message for the MatcherAgent
        test_message = {"content": input_data}  # Pass the loaded JSON as the content

        # Initialize the MatcherAgent
        matcher_agent = MatcherAgent()

        # Run the MatcherAgent with the loaded input data
        result = await matcher_agent.run([test_message])
        
        # Print the result to the console for verification
        print("\n🎯 Matcher Output:")
        print(result)

        # Save the result into a JSON file named 'matcher_output.json'
        with open("matcher_output.json", "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
            print("Output saved to 'matcher_output.json'.")

    except Exception as e:
        print(f"Error occurred: {e}")

# Execute the test function
if __name__ == "__main__":
    asyncio.run(test_matcher())
