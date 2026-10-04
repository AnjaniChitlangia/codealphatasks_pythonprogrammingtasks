"""
Basic Rule-Based Chatbot
------------------------
Replies to simple messages like "hi", "how are you" and "bye" with
pre-defined answers, and greets the user with good morning / afternoon /
evening based on the time each message is sent.
"""

import string
from datetime import datetime

BOT_NAME = "ChatBot"

GREETINGS = {"hi", "hello", "hey", "hii", "hola"}
GOODBYES = {"bye", "goodbye", "see you", "exit", "quit"}
GOOD_WORDS = {"good", "fine", "great", "well", "nice", "awesome", "happy", "okay", "ok"}
BAD_WORDS = {"bad", "sad", "tired", "not good", "not well", "terrible", "awful"}
THANKS = {"thanks", "thank you", "thx"}
QUESTIONS ={"help" ,"please","request"}

# Help requests and their pre-defined replies
HELP_REPLY = "Sure!"
HELP_REPLIES = {
    "can you please help me": HELP_REPLY,
    "can you help me": HELP_REPLY,
    "could you help me": HELP_REPLY,
    "please help me": HELP_REPLY,
    "i need help": HELP_REPLY,
    "help me": HELP_REPLY,
}

# When the user asks the bot to wait
WAIT_WORDS = {"wait", "hold on"}
WAIT_REPLY = "Yes sure! Waiting."


def time_greeting(now=None):
    """Return 'Good morning', 'Good afternoon' or 'Good evening'."""
    hour = (now or datetime.now()).hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    return "Good evening"


def clean(text):
    """Lowercase and remove punctuation so 'How are you?' matches 'how are you'."""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def contains_any(message, phrases):
    words = message.split()
    return any((p in message) if " " in p else (p in words) for p in phrases)


def get_reply(message, now=None):
    """Return (reply, should_exit) for a user message."""
    msg = clean(message)
    greeting = time_greeting(now)

    if not msg:
        return "Please type something :)", False
    if contains_any(msg, GOODBYES):
        return f"Goodbye! Have a {greeting.lower()}!", True
    if "how are you" in msg or "how r u" in msg:
        return "I am fine, thank you. What about you? How was your day?", False
    if "what are you doing" in msg or "what r u doing" in msg or "wyd" in msg.split():
        return "Waiting to help you!", False
    # Checked before help/"please" so "please wait" gets the wait reply
    if contains_any(msg, WAIT_WORDS):
        return WAIT_REPLY, False
    for phrase, reply in HELP_REPLIES.items():
        if phrase in msg:
            return reply, False
    if contains_any(msg, QUESTIONS):
        return HELP_REPLY, False
    if contains_any(msg, GREETINGS):
        return f"Hello! {greeting}!", False
    if contains_any(msg, THANKS):
        return "You're welcome!", False
    # Check "bad" before "good" so "not good" is treated as bad
    if contains_any(msg, BAD_WORDS):
        return "Sorry to hear that. I hope tomorrow is better!", False
    if contains_any(msg, GOOD_WORDS):
        return "That's great to hear!", False
    if "your name" in msg:
        return f"My name is {BOT_NAME}.", False
    return "Sorry, I didn't understand that. Try 'hi', 'how are you' or 'bye'.", False


def main():
    print(f"{BOT_NAME}: {time_greeting()}! I'm {BOT_NAME}. Type 'bye' to exit.")
    while True:
        try:
            user = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{BOT_NAME}: Goodbye!")
            break
        sent_at = datetime.now()
        reply, should_exit = get_reply(user, sent_at)
        print(f"{BOT_NAME} [{sent_at:%H:%M}]: {reply}")
        if should_exit:
            break


if __name__ == "__main__":
    main()
