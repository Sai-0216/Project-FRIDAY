import ollama


class AI:

    def ask(self, prompt: str) -> str:
        try:
            print("Calling Ollama...")

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print("Returned from Ollama")

            # New ollama package returns an object
            return response.message.content

        except Exception as e:
            print("AI Error:", repr(e))
            raise


ai = AI()