import ollama

print("Starting...")

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Say hello"
        }
    ]
)

print(response)