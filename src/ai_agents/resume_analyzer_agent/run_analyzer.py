import asyncio
import json
import os
from analyzer_agent import AnalyzerAgent

# Define input and output file paths
input_filepath = os.path.join("src", "ai_agents", "all_agents_v2", "extractor_output_1.json")
output_filepath = os.path.join("src", "ai_agents", "all_agents_v2", "analyzer_output_1.json")

# Create an instance of the AnalyzerAgent (only once)
analyzer_agent = AnalyzerAgent()

def load_input_from_file(file_path):
    """Load JSON input from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)  # No need for eval()
    except FileNotFoundError:
        print(f"❌ Error: Input file '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON from '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error loading '{file_path}': {e}")
        return None

async def test_analyzer():
    """Run the AnalyzerAgent on extracted resume data."""
    try:
        # Load input data
        input_data = load_input_from_file(input_filepath)
        if not input_data:
            print("⚠️ Error: Input data could not be loaded.")
            return
        
        print(f"📄 Loaded Input Data:\n{json.dumps(input_data, indent=4, ensure_ascii=False)}")  # Debug print

        # Ensure "structured_data" exists
        if "structured_data" not in input_data:
            print("❌ Error: Missing 'structured_data' key in input.")
            return

        # Prepare test message
        test_message = {"content": input_data}

        print(f"\n🚀 Running AnalyzerAgent with Input:\n{json.dumps(test_message, indent=4, ensure_ascii=False)}")  # Debug print

        # Run AnalyzerAgent
        result = await analyzer_agent.run([test_message])

        # Print the result for verification
        print("\n📊 **Analyzer Output:**\n", json.dumps(result, indent=4, ensure_ascii=False))

        # Save the result to the output file
        with open(output_filepath, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
            print(f"✅ Output saved to '{output_filepath}'.")

    except Exception as e:
        print(f"❌ Unexpected error occurred during analysis: {e}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
