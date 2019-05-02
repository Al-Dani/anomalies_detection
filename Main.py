'''!
    log preprocessing
    |
    model initialization
    |
    for each trace get conformance value
    |
    filter anomaly traces
    |
    classify anomaly traces
    |
    return .csv / .json for further visualization
'''

import EventsMatcher as match
import AttributePNet as pnet
import TokenReplay as replayer

import pandas as pd
import datetime as dt

MAX_INT = 100000


def _convert_time(time_str):
    return dt.datetime.strptime(time_str, "%d.%m.%Y").date()

def _preprocess(evlog):
    evlog['event_date'] = evlog['event_date'].apply(_convert_time)

    caseIds = evlog.UNIQ_ID.unique()
    logsDict = {elem: pd.DataFrame for elem in caseIds}

    for key in logsDict.keys():
        logsDict[key] = evlog[:][evlog.UNIQ_ID == key]

    return logsDict


def _create_net(attribute_petri_net, matcher):

    # add places
    places = matcher.places_to_text()
    for key in iter(places.keys()):
        attribute_petri_net.addPlace(key, False)
    attribute_petri_net.places['p4_1'].isFinal = True
    attribute_petri_net.places['p6_2'].isFinal = True
    attribute_petri_net.places['p7_1'].isFinal = True
    attribute_petri_net.places['p8_1'].isFinal = True

    # add transitions
    # Transition(name, fires, maxtime, hidden, weight)
    attribute_petri_net.addTransition('t1.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t1.2', 1, 100, False, 1)
    attribute_petri_net.addTransition('t2.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t2.1.1', 1, 100, False, 0.7)
    attribute_petri_net.addTransition('t2.2', 1, 100, True, 1)
    attribute_petri_net.addTransition('t3.1', 1, 100, True, 1)
    attribute_petri_net.addTransition('t3.2', MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t3.3', MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t4.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t4.2', 1, 100, False, 1)
    attribute_petri_net.addTransition('t4.3', MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t4.0', 2, 100, False, 0.9)
    attribute_petri_net.addTransition('t5.1', 1, 100, False, 0.8)
    attribute_petri_net.addTransition('t5.0', 1, 100, False, 1)
    attribute_petri_net.addTransition('t5.1.1', 1, 100, True, 1)
    attribute_petri_net.addTransition('t5.1.2', 1, 100, True, 1)
    attribute_petri_net.addTransition('t5.2', 10, 100, False, 1)
    attribute_petri_net.addTransition('t5.3', 1, 100, True, 1)
    attribute_petri_net.addTransition('t5.4', 1, 100, True, 1)
    attribute_petri_net.addTransition('t6.0', MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t6.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.2', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.3', 3, 100, False, 1)
    attribute_petri_net.addTransition('t6.4', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.5', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.3.1', 2, 100, False, 1)
    attribute_petri_net.addTransition('t7.0', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.1.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t6.2.1', 1, 100, False, 0.8)
    attribute_petri_net.addTransition('t7.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t7.2', 1, 100, False, 0.8)
    attribute_petri_net.addTransition('t8.1', 1, 100, False, 1)
    attribute_petri_net.addTransition('t9.1', MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t9.2', 1, 100, False, 0.8)

    # add arcs
    # addInputArc(self, placeName, transitionName):

    attribute_petri_net.addInputArc('start', 't1.1')
    attribute_petri_net.addInputArc('start', 't1.2')
    attribute_petri_net.addInputArc('start', 't7.0')
    attribute_petri_net.addInputArc('start', 't5.0')
    attribute_petri_net.addInputArc('p1_1', 't2.1')
    attribute_petri_net.addInputArc('p1_1', 't2.2')
    attribute_petri_net.addInputArc('final', 't2.1.1')
    attribute_petri_net.addInputArc('p2_1', 't3.1')
    attribute_petri_net.addInputArc('p2_1', 't3.2')
    attribute_petri_net.addInputArc('p2_1', 't3.3')
    attribute_petri_net.addInputArc('p3_1', 't4.0')
    attribute_petri_net.addInputArc('p3_1', 't4.1')
    attribute_petri_net.addInputArc('p3_1', 't4.2')
    attribute_petri_net.addInputArc('p3_1', 't4.3')
    attribute_petri_net.addInputArc('p4_1', 't5.1')
    attribute_petri_net.addInputArc('p5_0', 't5.1.1')
    attribute_petri_net.addInputArc('p5_0', 't5.1.2')
    attribute_petri_net.addInputArc('p4_2', 't5.2')
    attribute_petri_net.addInputArc('p4_2', 't5.3')
    attribute_petri_net.addInputArc('p5_1', 't6.0')
    attribute_petri_net.addInputArc('p5_1', 't6.1')
    attribute_petri_net.addInputArc('p5_1', 't6.2')
    attribute_petri_net.addInputArc('p5_1', 't6.3')
    attribute_petri_net.addInputArc('p5_1', 't6.4')
    attribute_petri_net.addInputArc('p5_1', 't6.5')
    attribute_petri_net.addInputArc('p6_1', 't6.1.1')
    attribute_petri_net.addInputArc('p6_2', 't6.2.1')
    attribute_petri_net.addInputArc('p6_3', 't6.3.1')
    attribute_petri_net.addInputArc('p6_3', 't7.1')
    attribute_petri_net.addInputArc('p6_3', 't7.2')
    attribute_petri_net.addInputArc('p7_1', 't8.1')
    attribute_petri_net.addInputArc('p8_1', 't9.1')
    attribute_petri_net.addInputArc('p8_1', 't9.2')

    #  addOutputArc(self, transitionName, placeName):
    attribute_petri_net.addOutputArc('t1.1', 'p1_1')
    attribute_petri_net.addOutputArc('t2.1', 'final')
    attribute_petri_net.addOutputArc('t1.2', 'p2_1')
    attribute_petri_net.addOutputArc('t2.2', 'p2_1')
    attribute_petri_net.addOutputArc('t3.1', 'p3_1')
    attribute_petri_net.addOutputArc('t3.2', 'p2_1')
    attribute_petri_net.addOutputArc('t3.3', 'p2_1')
    attribute_petri_net.addOutputArc('t4.1', 'final')
    attribute_petri_net.addOutputArc('t4.2', 'p4_1')
    attribute_petri_net.addOutputArc('t4.3', 'p4_2')
    attribute_petri_net.addOutputArc('t4.0', 'p2_1')
    attribute_petri_net.addOutputArc('t5.1', 'p5_0')
    attribute_petri_net.addOutputArc('t5.1.1', 'p2_1')
    attribute_petri_net.addOutputArc('t5.1.2', 'p4_2')
    attribute_petri_net.addOutputArc('t5.2', 'p2_1')
    attribute_petri_net.addOutputArc('t5.3', 'p5_1')
    attribute_petri_net.addOutputArc('t5.0', 'p5_1')
    attribute_petri_net.addOutputArc('t6.0', 'p5_1')
    attribute_petri_net.addOutputArc('t6.1', 'p6_1')
    attribute_petri_net.addOutputArc('t6.2', 'p6_2')
    attribute_petri_net.addOutputArc('t6.3', 'p6_3')
    attribute_petri_net.addOutputArc('t6.4', 'final')
    attribute_petri_net.addOutputArc('t6.3.1', 'p6_3')
    attribute_petri_net.addOutputArc('t7.0', 'p7_1')
    attribute_petri_net.addOutputArc('t7.1', 'p7_1')
    attribute_petri_net.addOutputArc('t6.5', 'p7_1')
    attribute_petri_net.addOutputArc('t7.2', 'p5_1')
    attribute_petri_net.addOutputArc('t6.1.1', 'p5_1')
    attribute_petri_net.addOutputArc('t6.2.1', 'p5_1')
    attribute_petri_net.addOutputArc('t8.1', 'p8_1')
    attribute_petri_net.addOutputArc('t9.1', 'final')
    attribute_petri_net.addOutputArc('t9.2', 'p6_3')


def main():
    matcher = match.Matcher()

    # Препроцессинг
    evlog = pd.read_csv("trial_log2.csv", sep=';')
    log_by_trace = _preprocess(evlog)

    # Инициализация модели
    # Нахождение значения conformance

    for trace in log_by_trace.keys():
        net = pnet.AttributePetriNet()
        _create_net(net, matcher)
        trace_replayer = replayer.TokenRaplay(net, matcher)
        trace_replayer.replay_log(log_by_trace[trace])
        conformance_value = format(trace_replayer.get_conformance(), '.3f')
        log_by_trace[trace]['conformance'] = conformance_value
        print(conformance_value)

    result_log = pd.concat(log_by_trace.values())
    result_log.to_csv("result2.csv", sep=';', index=False, encoding='mac_cyrillic')

    return


if __name__ == "__main__":
    main()
