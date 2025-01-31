import asyncio
import json
from extractor_agent import ExtractorAgent  # Adjust path if needed

# Create an instance of the ExtractorAgent
extractor_agent = ExtractorAgent()

# Prepare a test message. The message will likely contain the path to a file or resume data
test_message = {
    "content": {
        "file_path": "cleaned_resume.pdf"  # Path to the resume file
    }
}

# Run the extractor agent
async def test_extractor():
    try:
        # Run the agent with the test message
        result = await extractor_agent.run([test_message])
        
        # Print the result to the console for verification
        print(result)

        # Save the result into a JSON file named 'extractor_output.json'
        with open("extractor_output.json", "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
            print("Output saved to 'extractor_output.json'.")

    except Exception as e:
        print(f"Error occurred: {e}")


# Execute the test function
if __name__ == "__main__":
    asyncio.run(test_extractor())

