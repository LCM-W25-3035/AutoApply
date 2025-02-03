import asyncio
import json
import os
from extractor_agent import ExtractorAgent

# Define input and output file paths
input_filepath = os.path.join("src", "resumes", "resume_sample_3.pdf")  
output_filepath = os.path.join("src", "ai_agents", "pdf_extractor_agent", "extractor_output_3.json")  

# Create an instance of the ExtractorAgent
extractor_agent = ExtractorAgent()

# Prepare a test message with the input file path
test_message = {
    "content": {
        "file_path": input_filepath
    }
}

# Run the extractor agent
async def test_extractor():
    try:
        # Run the agent with the test message
        result = await extractor_agent.run([test_message])

        # Print the result to the console for verification
        print(result)

        # Save the result to the output file
        with open(output_filepath, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
            print(f"Output saved to '{output_filepath}'.")

    except Exception as e:
        print(f"Error occurred: {e}")


# Execute the test function
if __name__ == "__main__":
    asyncio.run(test_extractor())