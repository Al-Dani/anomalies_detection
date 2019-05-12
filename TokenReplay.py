import datetime as dt


def _check_inArcs(transition):
    enabled = True
    for key, value in transition.inArcs.items():
        if value.tokens == 0:
            enabled = False
    return enabled


def _is_loop(transition):
    return next(iter(transition.inArcs)) == next(iter(transition.outArcs))


def _check_fires(transition):
    if transition.firingCounter <= transition.legalFires:
        return 1.0
    return transition.legalFires/transition.firingCounter


def _get_hidden(place):
    hiddens = {}
    for key, transition in place.outArcs.items():
        if transition.hidden:
            hiddens[key] = transition
    return hiddens


class TokenRaplay(object):
    def __init__(self, net, matcher):
        self.net = net

        self.consumed = 0
        self.produced = 0
        self.miss = 0
        self.remain = 0

        self.marking = [self.net.startPlace]
        self.weight = 0
        self.count_transitions = 0

        self.matcher = matcher

    #ToDo: переписать token replay
    def replay_log(self, tracelog):
        current_model_position = self.net.startPlace
        row_counter = 0
        current_model_position.date = tracelog.iloc[row_counter]['event_date']

        while current_model_position != self.net.finishPlace and row_counter < tracelog.shape[0]:
            current_event = tracelog.iloc[row_counter]['event_type']
            current_event = current_event.strip()
            current_log_event = self.matcher.event_to_transition(current_event)

            if current_log_event in current_model_position.outArcs:
                current_transition = current_model_position.outArcs[current_log_event]
                if _check_inArcs(current_transition):
                    event_time = tracelog.iloc[row_counter]['event_date']
                    self.__check_time(current_model_position, current_transition, event_time)
                    self.__fire_token(current_transition, event_time)
                    self.__get_weight(current_transition)
                    row_counter = row_counter + 1
            else:
                list_hidden = _get_hidden(current_model_position)
                if len(list_hidden) == 1:
                    self.__fire_token(list_hidden[next(iter(list_hidden))], 0)
                else:
                    for key, transition in list_hidden.items():
                        if not _is_loop(transition):
                            self.__fire_token(transition)
            current_model_position = self.marking[0]

    def get_conformance(self):
        self.__check_remain()
        cost = self.__is_complete() * self.weight / self.count_transitions
        conformance = 0.5 * cost * (2 - self.miss/self.consumed + self.remain/self.produced)
        return conformance

    def __fire_token(self, transition, event_time):
        for key, place in transition.inArcs.items():
            place.remove_token()
            self.consumed = self.consumed + 1
            self.marking.remove(place)

        for key, place in transition.outArcs.items():
            place.add_token()
            self.produced = self.produced + 1
            if not transition.hidden and place.date == dt.date(dt.MINYEAR, 1, 1):
                place.date = event_time
            if transition.hidden:
                place.date = transition.inArcs[next(iter(transition.inArcs))].date
            self.marking.append(place)

        if not transition.hidden:
            self.count_transitions = self.count_transitions + 1
        transition.fire()

    def __get_weight(self, transition):
        self.weight = self.weight + _check_fires(transition) * transition.weight

    def __is_complete(self):
        if self.marking[0].isFinal:
            return 1
        return -1

    def __check_time(self, place, transition, event_time):
        if event_time - place.date > transition.maxTime:  # ToDO:пофиксить даты в hidden
            self.miss = self.miss + 1
            place.add_token()

    def __check_remain(self):
        for key, place in self.net.places.items():
            if place.tokens > 0 and not place.isFinal:
                self.remain = self.remain + 1
