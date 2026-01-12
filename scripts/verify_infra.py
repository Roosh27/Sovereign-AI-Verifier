import ollama

try:
    response = ollama.chat(model='phi3', messages=[
        {'role': 'user', 'content': 'Is the local infrastructure ready? Respond in 5 words.'},
    ])
    print("Ollama Connection:", response['message']['content'])
except Exception as e:
    print("Connection Failed. Make sure Ollama is running.")