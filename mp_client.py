# Author: TK
# Date: 21-01-2026
# Description: Client file to connect

import time
import socket
import threading
import json
from collections import deque

import pygame

from player import Player
from bullets import Bullet
from graphics_engine import GraphicsEngine

EXPECTED_PROTOCOL_VERSION = 1

# Net helpers
def send_json(sock: socket.socket, obj: dict):
    data = (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_lines(buffer: bytearray, data: bytes):
    buffer.extend(data)
    lines = []
    while True:
        idx = buffer.find(b"\n")
        if idx == -1:
            break
        line = buffer[:idx]
        del buffer[:idx + 1]
        if line:
            lines.append(line)
    return lines

# net client class
class NetworkClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = bytearray()
        self.running = False

        self.player_id = None
        self.tick_hz = None
        self.snapshot_hz = None
        self.world_w = None
        self.world_h = None

        self.lock = threading.Lock()
        self.snapshots = deque(maxlen = 30)
        self.seq = 0
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((self.host, self.port))
        self.running = True
        threading.Thread(target=self._reader, daemon = True).start()
        
    def close(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        
    def _reader(self):
        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    break

                for line in recv_lines(self.buffer, data):
                    try:
                        msg = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                    ty = msg.get("type")

                    if ty == "welcome":
                        server_protocol = int(msg.get("protocol", -1))

                        if server_protocol != EXPECTED_PROTOCOL_VERSION:
                            print(f"[CLIENT] Protocol mismatch. Server={server_protocol} Client={EXPECTED_PROTOCOL_VERSION}")
                            self.running = False
                            try:
                                self.sock.close()
                            except:
                                pass
                            return

                        self.player_id = int(msg["id"])
                        self.tick_hz = int(msg["tick_hz"])
                        self.snapshot_hz = int(msg["snapshot_hz"])
                        self.world_w = int(msg["w"])
                        self.world_h = int(msg["h"])

                        print(f"[CLIENT] Welcome id={self.player_id}")

                    elif ty == "snapshot":
                        with self.lock:
                            self.snapshots.append(msg)

                    else:
                        print("[CLIENT] Unknown msg type:", ty, msg)

        except (ConnectionResetError, OSError):
            pass
        finally:
            self.running = False


    def get_latest_snapshot(self):
        with self.lock:
            return self.snapshots[-1] if self.snapshots else None

    def send_input(self, up, down, left, right, shoot, angle):
        if not self.running:
            return
        self.seq += 1
        send_json(self.sock, {
            "type": "input",
            "seq": self.seq,
            "up": bool(up),
            "down": bool(down),
            "left": bool(left),
            "right": bool(right),
            "shoot": bool(shoot),
            "angle": float(angle),
        })


# View objects (client-side)

class RemotePlayerView:
    def __init__(self, pid: int):
        self.pid = pid
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.radius = 14
        self.hp = 100
        self.score = 0

    def apply(self, st: dict):
        self.x = float(st["x"])
        self.y = float(st["y"])
        self.angle = float(st["angle"])
        self.hp = int(st.get("hp", 100))
        self.score = int(st.get("score", 0))

class NPCView:
    def __init__(self, d: dict):
        self.x = float(d["x"])
        self.y = float(d["y"])
        self.radius = int(d.get("radius", 12))
        self.hp = int(d.get("hp", 1))
        self.hp_max = int(d.get("hp_max", 1))
        self.color = tuple(d.get("color", (200, 60, 60)))


# Main loop

def main():
    host = "127.0.0.1"
    port = 21001

    net = NetworkClient(host, port)
    net.connect()

    # wait for welcome 
    while net.running and net.player_id is None:
        time.sleep(0.01)

    if not net.running:
        return

    w = net.world_w or 1000
    h = net.world_h or 600

    gfx = GraphicsEngine(w, h, fps=60)
    player = Player(x=w/2, y=h/2, speed=260.0)  # local visual; server overwrites pos

    remote_players = {}
    npcs = []
    bullets = []
    particles = []

    running = True
    paused = False
    my_score = 0

    while running and net.running:
        dt = gfx.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # local rotate for responsiveness
        if not paused:
            rot_dir = 0
            if keys[pygame.K_LEFT]:
                rot_dir -= 1
            if keys[pygame.K_RIGHT]:
                rot_dir += 1
            if rot_dir != 0:
                player.rotate(rot_dir, dt)

            net.send_input(
                up=keys[pygame.K_w],
                down=keys[pygame.K_s],
                left=keys[pygame.K_a],
                right=keys[pygame.K_d],
                shoot=keys[pygame.K_SPACE],
                angle=player.angle,
            )

        snap = net.get_latest_snapshot()
        if snap and not paused:
            players = snap.get("players", {})
            my_id = net.player_id

            for pid_str, st in players.items():
                pid = int(pid_str)
                if pid == my_id:
                    player.x = float(st["x"])
                    player.y = float(st["y"])
                    player.angle = float(st["angle"])
                    my_score = int(st.get("score", 0))
                else:
                    rp = remote_players.get(pid)
                    if rp is None:
                        rp = RemotePlayerView(pid)
                        remote_players[pid] = rp
                    rp.apply(st)

            active = set(int(k) for k in players.keys())
            for pid in list(remote_players.keys()):
                if pid not in active:
                    del remote_players[pid]

            bullets = [Bullet.from_net(b) for b in snap.get("bullets", [])]
            npcs = [NPCView(d) for d in snap.get("npcs", [])]

        hud_data = {
            "score": my_score,
            "streak": 0,
            "mult": 1,
            "combo_ratio": 1.0,
            "paused": paused,
            "npc_count": len(npcs),
        }

        players_to_draw = [player] + list(remote_players.values())
        
        gfx.render(players_to_draw, npcs, bullets, particles, hud_data, offset=(0, 0))


    net.close()
    pygame.quit()

if __name__ == "__main__":
    main()
                    
