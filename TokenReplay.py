import AttributePNet as pNet


class TokenRaplay(object):
    def __init__(self, net):
        self.net = net

        self.consumed = 0
        self.produced = 0
        self.miss = 0
        self.remain = 0

    def replay_log(self, tracelog):
        current_model_position = self.net.startPlace
        current_log_event=tracelog.iloc[0]['event_type']

        for row_counter in range(tracelog.shape[0]):
