import datetime as dt
import Constants as cnst


def _check_inArcs(transition):
    """
    Check if all input places have tokens
    :param transition:
    :return: if the transition is enabled
    """
    enabled = True
    for key, value in transition.inArcs.items():
        if value.tokens == 0:
            enabled = False
    return enabled


def _is_loop(transition):
    """
    Check if the transition goes from and to the same place
    """
    return next(iter(transition.inArcs)) == next(iter(transition.outArcs))


def _check_fires(transition):
    if transition.firingCounter <= transition.legalFires:
        return 1.0
    return transition.legalFires/transition.firingCounter


def _get_hidden(place):
    """
    Get output transitions of a place that are marked as 'hidden'
    :param place:
    :return: list of hidden transitions
    """
    hiddens = {}
    for key, transition in place.outArcs.items():
        if transition.hidden:
            hiddens[key] = transition
    return hiddens


class TokenReplay(object):
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

        self.bag_of_transitions = ""

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

                    # add transition for further clustering
                    self.bag_of_transitions = self.bag_of_transitions + \
                                              self.matcher.transition_to_symbol(current_transition.name)
                    row_counter = row_counter + 1
            else:
                list_hidden = _get_hidden(current_model_position)
                if len(list_hidden) == 1:
                    self.__fire_token(list_hidden[next(iter(list_hidden))], 0)
                elif len(list_hidden) == 0:
                    current_transition = self.net.transitions[current_log_event]
                    self.bag_of_transitions = self.bag_of_transitions + cnst.SYMBOL_BAD + \
                                              self.matcher.transition_to_symbol(current_transition.name)

                    self.__fire_missing(current_transition)

                    self.marking.clear()  # assume that in one time only one place in marking
                    self.marking.append(current_model_position)  # we still in the same transition
                    row_counter = row_counter + 1
                else:
                    for key, transition in list_hidden.items():
                        if not _is_loop(transition):
                            self.__fire_token(transition)
            current_model_position = self.marking[0]

    def get_conformance(self):
        """
        Calculates weighted fitness metric
        :return: value of conformance for current trace
        """
        self.__check_remain()
        cost = self.__is_complete() * self.weight / self.count_transitions
        conformance = 0.5 * cost * (2 - self.miss/self.consumed - self.remain/self.produced)
        return conformance

    def __fire_token(self, transition, event_time):
        """
        Simulates transition firing. Consume tokens from all input places
        and produce tokens for all out places
        :param transition: firing transition
        :param event_time: datetime of a current event in a log
        """
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

    def __fire_missing(self, transition):
        for key, place in transition.inArcs.items():
            self.consumed = self.consumed + 1
            self.miss = self.miss + 1

        for key, place in transition.outArcs.items():
            place.add_token()
            self.produced = self.produced + 1

        if not transition.hidden:
            self.count_transitions = self.count_transitions + 1
        transition.fire()

    def __get_weight(self, transition):
        """
        Calculates a weight of a current transition firing according to model constraints
        """
        if transition.weight != 1:
            self.bag_of_transitions = self.bag_of_transitions + cnst.SYMBOL_BAD

        self.weight = self.weight + _check_fires(transition) * transition.weight

    def __is_complete(self):
        """
        Check if a final marking was reached
        :return: 1 if a trace is complete, -1 if a trace is incomplete
        """
        if self.marking[0].isFinal:
            return 1
        return -1

    def __check_time(self, place, transition, event_time):
        """
        Checks if a token is expired
        :param place: input place
        :param transition: firing transition
        :param event_time: log event datetime
        """
        if event_time - place.date > transition.maxTime:  # ToDO:пофиксить даты в hidden
            self.miss = self.miss + 1
            place.add_token()
            self.bag_of_transitions = self.bag_of_transitions + cnst.SYMBOL_TIME

    def __check_remain(self):
        """
        Calculates all missing tokens
        """
        for key, place in self.net.places.items():
            if place.tokens > 0 and not place.isFinal:
                self.remain = self.remain + 1

    def get_bag_of_transitions(self):
        return self.bag_of_transitions
