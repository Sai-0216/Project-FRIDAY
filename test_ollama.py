import ollama

print("Starting...")

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Return only this JSON: {\"intent\":\"volume_up\"}"
        }
    ]
)

print("Done!")
print(response)