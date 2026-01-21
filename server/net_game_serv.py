import socket
from threading import Thread

from games.characters import Player, NPC
from games.game_field import GameField
from server.server_game_engine import ServerGameEngine


def client_thread(conn, pid, engine):
    print(f"[SERVER] Client thread started for player {pid}", flush=True)

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print(f"[SERVER] Player {pid} disconnected", flush=True)
                break

            actions = eval(data.decode())
            engine.set_player_actions(pid, actions)

            state = engine.get_game_state_data()
            state["self"] = pid

            conn.sendall(str(state).encode())

        except Exception as e:
            print(f"[SERVER] Error with player {pid}: {e}", flush=True)
            break

    engine.remove_player(pid)
    conn.close()


def main():
    print("### SERVER FILE STARTED ###", flush=True)

    field = GameField(0, 0, 600, 600)
    engine = ServerGameEngine(field, [], [NPC(200, 200)])

    Thread(target=engine.run_game, daemon=True).start()

    s = socket.socket()
    s.bind(("0.0.0.0", 21002))
    s.listen()

    print("[SERVER] Listening on port 21002...", flush=True)

    pid = 0
    while True:
        conn, addr = s.accept()
        pid += 1

        print(f"[SERVER] Player {pid} connected from {addr}", flush=True)

        player = Player(pid, 100, 100)
        engine.add_player(player)

        Thread(
            target=client_thread,
            args=(conn, pid, engine),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()
