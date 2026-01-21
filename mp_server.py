# Author: TK
# Date: 21-01-2026
# Description: Server (TCP)

import socket
import threading
import time
import json
from typing import Dict, List

from npc import choose_npc_class
from constants import WORLD_W, WORLD_H, TICK_HZ, SNAPSHOT_HZ, PROTOCOL_VERSION
from server_world import World, InputState

# Net Helpers
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

class MultiplayerServer:
    """Multiplayer server using TCP sockets.
    - accepts multiple clients
    - receives input states
    - sends world snapshots
    - uses server_world.World for game logic
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 21001):
        self.host = host
        self.port = port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.world = World(WORLD_W, WORLD_H)
        
        self.lock = threading.Lock()
        self.clients: Dict[int, socket.socket] = {}
        self.buffers: Dict[int, bytearray] = {}
        self.inputs: Dict[int, InputState] = {}
        
        self.next_pid = 1
        self.running = True
        
    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"[GAME_SERVER] Listening on {self.host}:{self.port}")
        
        threading.Thread(target=self._accept_loop, daemon=True).start()
        self._tick_loop()
        
    def _accept_loop(self):
        while self.running:
            conn, addr = self.sock.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            with self.lock:
                pid = self.next_pid
                self.next_pid += 1
                
                self.clients[pid] = conn
                self.buffers[pid] = bytearray()
                self.inputs[pid] = InputState()
                
                self.world.add_player(pid)
                
            print(f"[GAME_SERVER] Player {pid} connected from {addr}")
            send_json(conn, {
                "type": "welcome",
                "protocol": PROTOCOL_VERSION,
                "id": pid,
                "tick_hz": TICK_HZ,
                "snapshot_hz": SNAPSHOT_HZ,
                "w": WORLD_W,
                "h": WORLD_H,
            })
        
            threading.Thread(target=self._client_reader, args=(pid, conn), daemon=True).start()
            
    def _client_reader(self, pid: int, conn: socket.socket):
        buf = self.buffers[pid]
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                for line in recv_lines(buf, data):
                    try:
                        msg = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                    if msg.get("type") == "input":
                        inp = InputState(
                            up = bool(msg.get("up")),
                            down = bool(msg.get("down")),
                            left = bool(msg.get("left")),
                            right = bool(msg.get("right")),
                            shoot = bool(msg.get("shoot")),
                            angle = float(msg.get("angle", 0.0)),
                            seq = int(msg.get("seq", 0)),
                        )
                        with self.lock:
                            self.inputs[pid] = inp
        except (ConnectionResetError, OSError):
            pass
        
        finally:
            print(f"[GAME_SERVER] Player {pid} disconnected")
            with self.lock:
                try:
                    conn.close()
                except:
                    pass
                self.clients.pop(pid, None)
                self.buffers.pop(pid, None)
                self.inputs.pop(pid, None)
                self.world.remove_player(pid)

    def _broadcast(self, obj: dict):
        dead = []
        with self.lock:
            for pid, conn in self.clients.items():
                try:
                    send_json(conn, obj)
                except OSError:
                    dead.append(pid)

            for pid in dead:
                try:
                    self.clients[pid].close()
                except:
                    pass
                self.clients.pop(pid, None)
                self.buffers.pop(pid, None)
                self.inputs.pop(pid, None)
                self.world.remove_player(pid)

    def _tick_loop(self):
        dt = 1.0 / TICK_HZ
        snapshot_every = max(1, int(TICK_HZ / SNAPSHOT_HZ))
        next_time = time.perf_counter()
        print("[GAME_SERVER] Tick loop started")

        while self.running:
            now = time.perf_counter()
            if now < next_time:
                time.sleep(max(0.0, next_time - now))
                continue
            next_time += dt

            with self.lock:
                inputs_copy = dict(self.inputs)

            # simulate (authoritative)
            self.world.step(dt, inputs_copy)

            if self.world.tick % snapshot_every == 0:
                snap = {"type": "snapshot", **self.world.snapshot()}
                self._broadcast(snap)

if __name__ == "__main__":
    MultiplayerServer().start()
        