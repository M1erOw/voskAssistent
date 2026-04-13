from commands.base import Command
from widgets.info_widget import InfoWidget

class Info(Command):
    def __init__(self):
        name = "справка"
        args = "-"
        description = "Показ окна с информацией о командах"
        super().__init__(name, args, description)
    
    def execute(self,args):
        self.info = InfoWidget()
        self.info.show()