import json
from typing import Optional
import datetime
def load_all(TICKETS_FILE="tickets.json"):
    try:
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []

def save_ticket(ticket: dict, TICKETS_FILE="tickets.json"):
    tickets = load_all(TICKETS_FILE)
    tickets.append(ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)
        
def add_new_chat(chat: dict, FILE="chat.json"):
    chats = load_all(FILE)
    chats.update(chat)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

def save_tickets(tickets, TICKETS_FILE="tickets.json"):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def get_ticket(ticket_id: str | int) -> Optional[dict]:
    tickets = load_all()
    ticket_id = int(ticket_id)
    for t in tickets:
        if t["ticket_id"] == ticket_id:
            return t
    return None

def update_ticket(updated_ticket: dict, status_file: str = None) -> None:
    if status_file:
        save_ticket(updated_ticket, status_file)

        tickets = load_all()
        tickets = [t for t in tickets if t["ticket_id"] != updated_ticket["ticket_id"]]
        save_tickets(tickets)
        return
    tickets = load_all()
    for idx, t in enumerate(tickets):
        if t["ticket_id"] == updated_ticket["ticket_id"]:
            tickets[idx] = updated_ticket
            break
    save_tickets(tickets)


def time_for_answer(ticket: dict):
    time_str = ticket.get("created_at")
    if not time_str:
        ticket["time_for_answer"] = "Неизвестно"
        return ticket

    try:
        time_dt = datetime.strptime(time_str, "%d.%m %H:%M")
    except Exception:
        ticket["time_for_answer"] = "Ошибка формата"
        return ticket

    now = datetime.now()
    delta = now - time_dt
    if delta.total_seconds() < 0:
        time_dt = time_dt.replace(year=datetime.now().year - 1)
        delta = now - time_dt
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    ticket["time_for_answer"] = f"{hours}ч {minutes}м"
    return ticket

def count_tickets(filename: str):
    try:
        with open(filename, "r", encoding="utf=8") as f:
            ticket = json.load(f)
            return len(ticket)
    except FileNotFoundError:
        return 0

def get_next_ticket_id(*file_names):
    total_tickets = 0
    for file_name in file_names:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                tickets = json.load(f)
                total_tickets += len(tickets)
        except FileNotFoundError:
            continue
    return total_tickets + 1

def get_chat():
    try:
        with open("chat.json", "r", encoding="utf-8") as f:
            chats = json.load(f)
        support_chats = {key: value["chat_id"] for key, value in chats.items()}
        messages = {key: value["message"] for key, value in chats.items()}
        return support_chats, messages
    except FileNotFoundError:
        print("Файл не найден")
        return {}, {}

def delete_chat(chat_name: str, file_path: str = "chat.json") -> bool:

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if chat_name not in data:
            print(f"⚠️ Чат '{chat_name}' не найден.")
            return False

        del data[chat_name]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Чат '{chat_name}' успешно удалён.")
        return True

    except json.JSONDecodeError:
        print("❌ Ошибка: JSON повреждён или пуст.")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
