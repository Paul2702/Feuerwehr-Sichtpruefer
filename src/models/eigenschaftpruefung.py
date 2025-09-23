from src.models.eigenschaft import Eigenschaft


class Eigenschaftspruefung:
    def __init__(self, eigenschaft: Eigenschaft, keinHandlungsbedarf = True, massnahmen = ''):
        self.eigenschaft = eigenschaft
        self.keinHandlungsbedarf = keinHandlungsbedarf
        self.massnahmen = massnahmen
    
    def setKeinHandlungsbedarf(self, keinHandlungsbedarf: bool):
        self.keinHandlungsbedarf = keinHandlungsbedarf
    
    def setMassnahmen(self, massnahmen: str):
        self.massnahmen = massnahmen