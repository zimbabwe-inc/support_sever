import json 

def count_tickets(filename: str):
    try:
        with open(filename, "r", encoding="utf=8") as f:
            ticket = json.load(f)
            return len(ticket)
    except FileNotFoundError:
        return 0
print("Новых тикетов:", count_tickets("tickets.json"))
print("Решённых тикетов:", count_tickets("resolved_tickets.json"))
print("Отклонённых тикетов:", count_tickets("rejected_tickets.json"))