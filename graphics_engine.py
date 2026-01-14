# Author: TK
# Date: 2024-06-10
# Description: Graphic engine class
import os
from typing import Iterable, List, Optional
class GraphicsEngine:
    def __init__(self, clear_each_frame: bool = True, empty_char: str = "."):
        self.clear_each_frame = clear_each_frame
        self.empty_char = empty_char
        
    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
    
    def render(self, 
               width: int,
               height: int,
               entities: Iterable, 
               hud_lines: Optional[List[str]] = None) -> None:
        if self.clear_each_frame:
            self.clear()
            
        grid = [[self.empty_char for _ in range(width)] for _ in range(height)]
        
        # New entities overwrite old ones
        for e in entities:
            x, y = int(e.x), int(e.y)
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = str(e.char)[0] # force 1 char
                
        for row in grid:
            print("".join(row))
            
        if hud_lines:
            print()
            for line in hud_lines:
                print(line)