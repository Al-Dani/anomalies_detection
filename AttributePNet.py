import datetime

class Place (object):
    '''!
    Class to represent a place in a Petri Net
    Tokens are represented by Integer values
    input and output arcs are represented as sets of possible transitions
    date attribute refers to a timestamp - дата первого перехода в позицию --- ЗАЧЕМ ТУТ??
    isFinal - specify if this place can be final
    '''
    def __init__(self, name, final, tokens=0):
        '''!
            Constructor method.

            @param name: name of the place
            @param final: specify if this place can be final
        '''
        self.name = str(name)
        self.tokens = tokens
        self.inArcs = {}
        self.outArcs = {}
        self.date = datetime.date(datetime.MINYEAR, 1, 1) # ?????
        self.isFinal = final

    def add_token(self):
        self.tokens = self.tokens + 1

    def remove_token(self):
        self.tokens = self.tokens - 1

    def set_date(self, timestamp):
        self.date = datetime.datetime.strptime(timestamp, "%d.%m.%y")


class Transition (object):
    '''!
    Class to represent a transition ib a Petri Net
    '''

    def __init__(self, name, fires, maxtime, hidden, weight=1):
        '''!
                Constructor method.

                @param name: name of the transition
                @param fires: legal number of firing for the transition
                @param maxtime: legal gap before transition firing
                @param weight: penalty for transition firing
        '''
        self.name = str(name)
        self.inArcs = {}
        self.outArcs = {}
        self.legalFires = fires
        self.firingCounter = 0
        self.maxTime = datetime.timedelta(days=maxtime)
        self.weight = weight
        self.hidden = hidden

    def fire(self):
        self.firingCounter = self.firingCounter + 1


class AttributePetriNet (object):
    def __init__(self):
        self.startPlace = Place("start", False, tokens=1)
        self.finishPlace = Place("final", True)
        self.places = {
            "start": self.startPlace,
            "final": self.finishPlace
        }
        self.transitions = {}

    def addPlace(self, name, final):
        newPlace = Place(name, final)
        self.places[name] = newPlace

    def addTransition (self, name, fires, maxtime, hidden, weight):
        newTransition = Transition(name, fires, maxtime, hidden, weight)
        self.transitions[name] = newTransition

    def addInputArc(self, placeName, transitionName):
        '''!
                Method that add arcs from place to transition
        '''
        currentPlace = self.places[placeName]
        currentTransition = self.transitions[transitionName]
        currentPlace.outArcs[transitionName] = currentTransition
        currentTransition.inArcs[placeName] = currentPlace

    def addOutputArc(self, transitionName, placeName):
        '''!
                Method that add arcs from transitions to places
        '''
        currentPlace = self.places[placeName]
        currentTransition = self.transitions[transitionName]
        currentPlace.inArcs[transitionName] = currentTransition
        currentTransition.outArcs[placeName] = currentPlace
