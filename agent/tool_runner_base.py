from abc import ABC, abstractmethod

class ToolRunner(ABC):
    def __init__(self, file_path, out):
        self.file_path = file_path
        self.out = out
    
    @abstractmethod
    def run(self):
        pass