import abc


class CustomPantryHandler(metaclass=abc.ABCMeta):

    def __init__(self, state):
        self.state = state

    @abc.abstractmethod
    def process_event(self, event, task):
        pass
