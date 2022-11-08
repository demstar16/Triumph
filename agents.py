from pyprobs import Probability

#Base class for the other agents
class Agent:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name


#Class for each member of the green population
class Green(Agent):
    def __init__(self, name, uncertainty, voteStatus):
        super().__init__(name)
        self.uncertainty = uncertainty
        self.voteStatus = voteStatus

    def changeVoteStatus(self, voteStatus):
        self.voteStatus = voteStatus

#Class for the Red Agent
class Red(Agent):
    def __init__(self, name):
        super().__init__(name)

    def setUncertainty(self, uncertainty):
        self.uncertainty = uncertainty

    def changeUncertainty(self, uncertaintyChange):
        self.uncertainty += uncertaintyChange
        if self.uncertainty > 1:
            self.uncertainty = 0.95
        if self.uncertainty < 0:
            self.uncertainty = 0.05

#Class for the Blue Agent
class Blue(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.energy = 100
        self.usrEnergy = 100

    def useEnergy(self, energy_used):
        self.energy -= energy_used
    
    def useUserEnergy(self, energy_used):
        self.usrEnergy -= energy_used

    def setUncertainty(self, uncertainty):
        self.uncertainty = uncertainty

    def changeUncertainty(self, uncertaintyChange):
        self.uncertainty += uncertaintyChange
        if self.uncertainty > 1:
            self.uncertainty = 0.95
        if self.uncertainty < 0:
            self.uncertainty = 0.05
    
#Class for the Grey agents
class Grey(Agent):
    def __init__(self, name):
        super().__init__(name)

    def changeBetrayProb(self, betray):
        self.betray = betray

    

