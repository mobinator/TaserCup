import time

from Cup import Cup


def start_countdown():
    for i in range(3):
        print(i)
        time.sleep(1)


class RaceGame:

    def __init__(self, cups: list):
        self.cups = cups
        self.finished_cups = []

    def start_game(self):
        start_countdown()
        print("Game started")
        for cup in self.cups:
            print(cup)
        print("Game ended")
        return True

    def set_cup_state(self, cup_id: int, state: str):
        for cup in self.cups:
            if cup.id == cup_id:
                cup.state = state
                if state == "finished":
                    self.finished_cups.append(cup)
                return True
        return False
