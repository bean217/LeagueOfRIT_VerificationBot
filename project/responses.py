def handle_join(user) -> str:
    return f'{user}, welcome to League of RIT! ' + \
        "Please answer the following set of questions to verify yourself."

def handle_response(message) -> str:
    p_message = message.lower()
    return "Sorry, I didn't understand your response."