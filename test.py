import json 

def get_chat():
    try:
        with open("chat.json", "r", encoding="utf-8") as f:
            chats = json.load(f)
        return {key: value["chat_id"] for key, value in chats.items()}
    except FileNotFoundError:
        print("Файл не найден")
        return {}

def load_support_chats(file_name="chat.json"):
    try:
        with open("chat.json", "r", encoding="utf-8") as f:
            chats = json.load(f)
        support_chats = {key: value["chat_id"] for key, value in chats.items()}
        messages = {key: value["message"] for key, value in chats.items()}
        return support_chats, messages
    except FileNotFoundError:
        print(f"Файл {file_name} не найден")
        return {}, {}

print(get_chat(), load_support_chats())