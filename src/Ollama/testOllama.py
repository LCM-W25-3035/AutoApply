import ollama

desiredModel='llama3.1:8b'
questionToAsk='What is the capital of colombia'

response = ollama.chat(model=desiredModel,messages=[
    {
        'role': 'user',
        'content': questionToAsk
    }
])

ollamaResponse=response['message']['content']

print(ollamaResponse)

with open('OutputOllama.txt',"w") as text_file:
    text_file.write(ollamaResponse)
