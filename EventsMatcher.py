import pandas as pd


class Matcher(object):
    def __init__(self):
        df = pd.read_csv("events_to_transitions 2.csv", sep=';')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        event_list = df['event'].tolist()
        # event_list = map(str.strip, event_list)
        transition_id_list = df['transition_id'].tolist()
        #ctransition_id_list = map(str.strip, transition_id_list)
        self.events_to_transitions = dict(zip(event_list, transition_id_list))
        self.transition_id = transition_id_list

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
