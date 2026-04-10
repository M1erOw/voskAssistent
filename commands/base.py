from abc import ABC,abstractmethod

class Command(ABC):
    def __init__(self,name,args,description):
        self.name = name
        self.args = args
        self.description = description

    @abstractmethod
    def execute(self, args):
        pass