'''!
    log preprocessing - DONE
    |
    model initialization - DONE
    |
    for each trace get conformance value - DONE
    |
    filter anomaly traces - DONE
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
import Constants as cnst


def _convert_time(time_str):
    return dt.datetime.strptime(time_str, "%d.%m.%Y").date()


def _preprocess(evlog):
    evlog['event_date'] = evlog['event_date'].apply(_convert_time)

    caseIds = evlog.UNIQ_ID.unique()
    logsDict = {elem: pd.DataFrame for elem in caseIds}

    for key in logsDict.keys():
        logsDict[key] = evlog[:][evlog.UNIQ_ID == key]

    return logsDict


def _find_cycle(word):
    if len(word) < 4:
        return word

    initial = word
    word = word.replace(cnst.SYMBOL_BAD, "")
    is_cycle = False
    cycle_count = 0
    cycle_symbols = ""
    result = ""
    has_cycle = False

    i = 0
    while i < len(word)-3:
        current = word[i:i+2]
        current_next = word[i+2:i+4]
        if current == current_next:
            has_cycle = True
            if not is_cycle:
                cycle_count = 1
                is_cycle = True
                cycle_symbols = current
            cycle_count = cycle_count + 1
            i = i + 2
        else:
            if is_cycle:
                result = result + cnst.SYMBOL_LOOP_START + cycle_symbols + str(cycle_count)
                is_cycle = False
                cycle_symbols = ""
                cycle_count = 0
                i = i + 2
            else:
                result = result + word[i]
                i = i + 1

    result = result + word[-3:]
    if has_cycle:
        return result
    else:
        return initial


def _create_net(attribute_petri_net, matcher):

    # add places
    places = matcher.places_to_text()
    for key in iter(places.keys()):
        attribute_petri_net.addPlace(key, False)
    attribute_petri_net.places['p4_1'].isFinal = True
    attribute_petri_net.places['p6_1'].isFinal = True
    attribute_petri_net.places['p6_2'].isFinal = True
    attribute_petri_net.places['p7_1'].isFinal = True
    attribute_petri_net.places['p8_1'].isFinal = True

    # add transitions
    # Transition(name, fires, maxtime, hidden, weight)
    attribute_petri_net.addTransition('t1.1', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t1.2', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t2.1', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t2.1.1', 1, cnst.MAX_INT, False, 0.7)
    attribute_petri_net.addTransition('t2.2', 1, cnst.MAX_INT, True, 1)  # no
    attribute_petri_net.addTransition('t3.1', 1, cnst.MAX_INT, True, 1)  # no
    attribute_petri_net.addTransition('t3.2', cnst.MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t3.3', cnst.MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t4.1', 1, 30, False, 1)
    attribute_petri_net.addTransition('t4.2', 1, 30, False, 1)  # отказать в возбуждении УД
    attribute_petri_net.addTransition('t4.3', cnst.MAX_INT, 30, False, 1)  # возбуждено УД
    attribute_petri_net.addTransition('t4.0', 2, 180, False, 1)  # доследственная проверка продлена
    attribute_petri_net.addTransition('t5.1', 1, cnst.MAX_INT, False, 0.8)
    attribute_petri_net.addTransition('t5.0', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t5.1.1', 1, cnst.MAX_INT, True, 1)  # no
    attribute_petri_net.addTransition('t5.1.2', 1, cnst.MAX_INT, True, 1)  # no
    attribute_petri_net.addTransition('t5.2', 10, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t5.3', 1, 30, True, 1)
    attribute_petri_net.addTransition('t5.4', 1, cnst.MAX_INT, True, 1)
    attribute_petri_net.addTransition('t6.0', cnst.MAX_INT, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t6.1', 1, cnst.MAX_INT, False, 1)  # дело приостановлено
    attribute_petri_net.addTransition('t6.2', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t6.3', 3, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t6.4', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t6.5', 1, cnst.MAX_INT, False, 1)
    attribute_petri_net.addTransition('t6.3.1', 2, 100, False, 1)
    attribute_petri_net.addTransition('t7.0', 1, cnst.MAX_INT, False, 1)  # дело частного обвинения
    attribute_petri_net.addTransition('t6.1.1', 1, 60, False, 1)  # возобновить приостановленное
    attribute_petri_net.addTransition('t6.2.1', 1, 100, False, 0.8)
    attribute_petri_net.addTransition('t7.1', 1, 10, False, 1)  # прокурор направил дело в суд
    attribute_petri_net.addTransition('t7.2', 1, 10, False, 0.8)  # прокурор вернул дело
    attribute_petri_net.addTransition('t8.1', 1, 24, False, 1)  # дело рассмотрено судом
    attribute_petri_net.addTransition('t9.1', cnst.MAX_INT, 100, False, 1)
    attribute_petri_net.addTransition('t9.2', 1, 100, False, 0.8)  # 34

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

    trans_list = matcher.get_trans_to_symb()
    print("символьные соответствия:")
    print(trans_list)

    # Препроцессинг
    evlog = pd.read_csv("trial_log3.csv", sep=';', encoding='mac_cyrillic')
    log_by_trace = _preprocess(evlog)

    list_of_traces = []

    # Инициализация модели
    # Нахождение значения conformance

    for trace in log_by_trace.keys():
        net = pnet.AttributePetriNet()
        _create_net(net, matcher)
        trace_replayer = replayer.TokenReplay(net, matcher)
        trace_replayer.replay_log(log_by_trace[trace])

        conformance = trace_replayer.get_conformance()
        conformance_value = format(conformance, '.3f')
        log_by_trace[trace]['conformance'] = conformance_value
        print(conformance_value)

        if conformance < 1:
            word = trace_replayer.get_bag_of_transitions()
            word_with_cycle = _find_cycle(word)
            list_of_traces.append(word_with_cycle)
            print(word_with_cycle)

    result_log = pd.concat(log_by_trace.values())
    result_log.to_csv("result3.csv", sep=';', index=False, encoding='mac_cyrillic')

    return


if __name__ == "__main__":
    main()
