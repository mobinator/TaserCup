

def add_cup(ip: str, cups: dict):
    cup_ips = [cup.ip for cup in cups]
    cup_id = len(cups) + 1
    if ip not in cup_ips:
        cup = Cup(cup_id, ip)
        cups[cup_id] = cup
        return cup


class Cup:

    def __init__(self, cup_id: int, ip: str):
        self.id = cup_id
        self.ip = ip

    def __str__(self):
        return f"Cup {self.id} with IP {self.ip}"

