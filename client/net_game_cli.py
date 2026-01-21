import socket

from games.graphics_engine import PyGameGraphicsEngine
from games.input_controller import PyGameInputController

HOST = "127.0.0.1"
PORT = 21001

s = socket.socket()
s.connect(("127.0.0.1", 21002))
print("Connected")

gfx = PyGameGraphicsEngine(600, 600)
inp = PyGameInputController()

while True:
    keys = inp.get_pressed_keys()

    if "q" in keys:
        break

    actions = {k: True for k in keys}
    s.send(str(actions).encode())

    state = eval(s.recv(2048).decode())

    gfx.start_frame()

    for pid, (x, y, _) in state["players"].items():
        color = "green" if pid == state["self"] else "blue"
        gfx.render_circle(x, y, 10, color)

    for x, y in state["npcs"]:
        gfx.render_circle(x, y, 10, "red")

    gfx.show_frame()
