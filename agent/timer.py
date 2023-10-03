from datetime import timedelta
import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.execution_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time

    def formatted_time(self):
        if self.execution_time is None:
            return "Timer não iniciado ou detido."
        
        hours, remainder = divmod(int(self.execution_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def as_timedelta(self):
        if self.execution_time is None:
            return None

        return timedelta(seconds=self.execution_time)