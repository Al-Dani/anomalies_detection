import pandas as pd
import string

class Matcher(object):
    def __init__(self):
        df = pd.read_csv("events_to_transitions 2.csv", sep=';')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        event_list = df['event'].tolist()
        transition_id_list = df['transition_id'].tolist()

        self.events_to_transitions = dict(zip(event_list, transition_id_list))
        self.transition_id = (list(set(transition_id_list)))
        self.transitions_to_symbols = {}

        # __transition_to_symbol(self):
        list_of_transitions = self.transition_id
        # add hidden transitions
        list_of_transitions.append('t2.2')
        list_of_transitions.append('t3.1')
        list_of_transitions.append('t5.1.1')
        list_of_transitions.append('t5.1.2')

        list_of_symbols = list(string.ascii_letters)[:len(list_of_transitions)]
        self.transitions_to_symbols = dict(zip(list_of_transitions, list_of_symbols))  # encode
        self.symbols_to_transitions = dict(zip(list_of_symbols, list_of_transitions))  # decode

    def event_to_transition(self, evname):
        return self.events_to_transitions[evname]

    def places_to_text(self):
        places_dict = {
            'p1_1': 'Сообщение о происшествии',
            'p2_1': 'Сообщение о преступлении',
            'p3_1': 'Результат доследственной проверки',
            'p4_1': 'Отказано в возбуждении уголовного дела',
            'p4_2': 'Возбуждено уголовное дело',
            'p5_0': 'Отказ отменен',
            'p5_1': 'Дело в производстве',
            'p6_1': 'Дело приостановлено',
            'p6_2': 'Делопроизводство прекращено',
            'p6_3': 'Дело на рассмотрении у прокурора',
            'p7_1': 'Дело в суде',
            'p8_1': 'Решение суда'
        }
        return places_dict

    def transition_to_symbol(self, transition_name):
        return self.transitions_to_symbols[transition_name]

    def get_trans_to_symb(self):
        return self.transitions_to_symbols

    def get_symbols_to_trans(self):
        return self.symbols_to_transitions
