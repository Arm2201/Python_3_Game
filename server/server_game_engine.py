import time

class ServerGameEngine:
    def __init__(self, game_field, players, npcs, fps=60):
        self.game_field = game_field
        self.players = players
        self.npcs = npcs
        self.fps = fps
        self.actions_for_players = {}

    def set_player_actions(self, pid, actions):
        self.actions_for_players[pid] = actions

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, pid):
        self.players = [p for p in self.players if p.id != pid]

    def get_game_state_data(self):
        return {
            "players": {
                p.id: (p.x, p.y, p.score)
                for p in self.players
            },
            "npcs": [(n.x, n.y) for n in self.npcs]
        }

    def update_state(self):
        for npc in self.npcs:
            npc.move(self.game_field)

        for p in self.players:
            a = self.actions_for_players.get(p.id, {})
            p.move(
                a.get("left", False),
                a.get("right", False),
                a.get("up", False),
                a.get("down", False),
                False,
                self.game_field
            )

    def run_game(self):
        print("[SERVER] Game loop running")
        while True:
            self.update_state()
            time.sleep(1 / self.fps)
