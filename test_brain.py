from brain import brain

while True:
    command = input("You: ")

    if not brain.process(command):
        break