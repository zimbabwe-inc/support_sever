import json
from typing import Optional

def load_tickets(TICKETS_FILE="tickets.json"):
    try:
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} 

def save_ticket(ticket: dict, TICKETS_FILE="tickets.json"):
    tickets = load_tickets()
    tickets.append(ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def save_tickets(tickets, TICKETS_FILE="tickets.json"):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def get_ticket(ticket_id: str | int) -> Optional[dict]:
    tickets = load_tickets()
    ticket_id = int(ticket_id)
    for t in tickets:
        if t["ticket_id"] == ticket_id:
            return t
    return None

def update_ticket(updated_ticket: dict) -> None:
    tickets = load_tickets()
    for idx, t in enumerate(tickets):
        if t["ticket_id"] == updated_ticket["ticket_id"]:
            tickets[idx] = updated_ticket
            break
    save_tickets(tickets)
