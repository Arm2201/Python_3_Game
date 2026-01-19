class ScoreSystem:
    """Track score, hit streak, and score multiplier
        
       Conditions:
       1. If you hit another NPC within comnbo_window seconds, streak increases.
       2. If you take too long between hits, streak resets.
       3. Multiplier increases every 'streak_step' hits, capped at 'max_multiplier'"""
       
    def __init__(self, combo_window: float = 1.25, streak_step: int = 5, max_multiplier: int = 6):
        self.score = 0
        self.streak = 0
        self.last_hit_time = None
        
        self.combo_window = combo_window
        self.streak_step = streak_step
        self.max_multiplier = max_multiplier
        
    def update_time(self, now: float) -> None:
        # If too much time passes since last hit, streak dies
        if self.last_hit_time is not None and (now - self.last_hit_time) > self. combo_window:
            self.streak = 0
            
            
    def multiplier(self) -> int:
        # 0-4 streak = 1x, 5-9 = 2x, 10-14 = 3x
        m = 1 + (self.streak // self.streak_step)
        return min(m, self.max_multiplier)
    
    def combo_ratio(self, now: float) -> float:
        """Returns 0..1 for the streak time bar.
        1 means fresh combo time remaining, 0 means combo expired."""
        if self.last_hit_time is None or self.streak <= 0:
            return 0.0
        elapsed = now - self.last_hit_time
        remaining = self.combo_window
        if remaining <= 0:
            return 0.0
        return max(0.0, min(1.0, remaining / self.combo_window))
        
    def on_hit(self, now: float, base_points: int) -> int:
        # called whenever you successfully hit and destroy an NPC
        if self.last_hit_time is None or (now - self.last_hit_time) > self.combo_window:
            self.streak = 1
        else:
            self.streak += 1
            
        self.last_hit_time = now
        gained = base_points * self.multiplier()
        self.score += gained
        return gained