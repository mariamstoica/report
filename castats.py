#!/usr/bin/env python

import logging
from pprint import pformat

class CAStats:
    def __init__(self, history, values):
        self.history = history
        self.values = values  # dict id->value

    def total_utility(self, id, verbose=False):
        def util(t):
            round = self.history.round(t)
            agent_payment = 0
            for i in range(0, len(round.payments)):
                if round.payments[i][0] == id:
                    agent_payment = round.payments[i][1]

            if agent_payment == 0:
                return 0
            else:
                this_agent_bids = filter(lambda a : a[0] == id, round.allocation)
                agent_value = 0
                for bid in this_agent_bids:
                    agent_value += sum([self.values[id][i]*bid[1][i] for i in range(0, len(bid[1]))])
                return agent_value - agent_payment

            # if id not in round.occupants:
            #     # Didn't get a slot in this round
            #     return 0
            # slot = round.occupants.index(id)
            # return round.clicks[slot] * (
            #     self.values[id] - round.per_click_payments[slot])

        rounds = self.history.num_rounds()
        if(verbose):
            logging.info("%d: utils: %s\n" % (id, str(list(util(t) for t in range(rounds)))))
            logging.info("%d: values = %s" % (id, self.values[id]))
        
        return sum(util(t) for t in range(rounds))

    def total_revenue(self):
        rev = 0
        def round_payment(allocation):
            payment = 0
            for i in range(0, len(allocation)):
                payment += allocation[i][2]
            return payment

        for i in range(self.history.num_rounds()):
            r = self.history.round(i)
            rev += round_payment(r.allocation)
        return rev

    def __repr__(self):
        return "Stats(history with %d rounds, vals %s)" % (
            self.history.last_round() + 1,
            str(self.values))