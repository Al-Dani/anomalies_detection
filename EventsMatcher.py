import pandas as pd


class Matcher(object):
    def __init__(self):
        df = pd.read_csv("events_to_transitions.csv", sep=';')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        event_list = df['event'].tolist()
        transition_id_list = df['transition_id'].tolist()
        self.events_to_transitions = dict(zip(event_list,transition_id_list))

    def event_to_transition(self, evname):
        return self.events_to_transitions[evname]
