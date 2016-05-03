#!/usr/bin/env python

import sys

class FinalTruthful:
    """Truthful bidding"""
    def __init__(self, id, values, demands):
        self.id = id
        self.values = values
        self.demands = demands

    def initial_bid(self):
        return (self.id, self.demands, sum([self.values[i]*self.demands[i] for i in range(0, len(self.values))]))

    def bid(self, t, history):
        return self.initial_bid()

# class DerBoobb4:
#     """Balanced bidding agent"""
#     def __init__(self, id, value, budget):
#         self.id = id
#         self.value = value
#         self.budget = budget

#     def initial_bid(self, reserve):
#         return self.value / 2

#     def slot_info(self, t, history, reserve):
#         """Compute the following for each slot, assuming that everyone else
#         keeps their bids constant from the previous rounds.

#         Returns list of tuples [(slot_id, min_bid, max_bid)], where
#         min_bid is the bid needed to tie the other-agent bid for that slot
#         in the last round.  If slot_id = 0, max_bid is 2* min_bid.
#         Otherwise, it's the next highest min_bid (so bidding between min_bid
#         and max_bid would result in ending up in that slot)
#         """
#         prev_round = history.round(t-1)
#         other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

#         clicks = prev_round.clicks
#         def compute(s):
#             (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
#             if max == None:
#                 max = 2 * min
#             return (s, min, max)

#         info = map(compute, range(len(clicks)))
# #        sys.stdout.write("slot info: %s\n" % info)
#         return info

#     def expected_utils(self, t, history, reserve):
#         """
#         Figure out the expected utility of bidding such that we win each
#         slot, assuming that everyone else keeps their bids constant from
#         the previous round.

#         returns a list of utilities per slot.
#         """
#         # TODO: Fill this in
#         #From the history, find the click values and other bids
#         prev_round = history.round(t-1)
#         clicks = prev_round.clicks
#         other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

#         #Sort other_bids by bid value

#         other_bids.sort(key=lambda bid: bid[1], reverse=True)

#         #The utility of position j (0-indexed) is the click value
#         #clicks[j] * (value minus other_bid[j]), as we are finding the
#         #expected utility of beating that bid, meaning we'd have
#         #to pay the amount of that bid.  Also, the number of positions
#         #is one less than the number of bids, so it is the length of the
#         #other_bids array

#         num_positions = len(other_bids)

#         utilities = []
#         for i in range(0, num_positions):
#             utilities.append(clicks[i]*(self.value-other_bids[i][1]))

#         return utilities

#     def target_slot(self, t, history, reserve):
#         """Figure out the best slot to target, assuming that everyone else
#         keeps their bids constant from the previous rounds.

#         Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
#         the other-agent bid for that slot in the last round.  If slot_id = 0,
#         max_bid is min_bid * 2
#         """
#         i =  argmax_index(self.expected_utils(t, history, reserve))
#         info = self.slot_info(t, history, reserve)
#         return info[i]

#     def bid(self, t, history, reserve):
#         # The Balanced bidding strategy (BB) is the strategy for a player j that, given
#         # bids b_{-j},
#         # - targets the slot s*_j which maximizes his utility, that is,
#         # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
#         # - chooses his bid b' for the next round so as to
#         # satisfy the following equation:
#         # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
#         # (p_x is the price/click in slot x)
#         # If s*_j is the top slot, bid the value v_j

#         prev_round = history.round(t-1)
#         (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

#         # TODO: Fill this in.
#         #Here, our bidding agent needs to be able to understand when the VCG
#         #mechanism is being used, it should bid truthfully, but under GSP
#         #it should use balanced bidding.

#         if t >= 24:
#             bid = self.value
#         else:

#             #If the min_bid is greater than or equal to the value at this position,
#             #just bid the value to the bidder.

#             if min_bid >= self.value:
#                 bid = self.value

#             #Otherwise, if the position we're aiming for is first place, just bid
#             #our value
#             elif slot == 0:
#                 bid = self.value

#             #Finally, if neither condition is met we need to choose the balanced
#             #bidding value.  Since click rate is multiplied by 0.75 for each
#             #position, we need to solve the equation 0.75(value-min_bid) = 1(value-newbid).
#             #This is because min_bid is calculated to be the bid below you, so you'd
#             #have to pay that price in that position.
#             #So, newbid = 0.25*value+0.75*min_bid, which we'll round to the nearest
#             #integer.

#             else:
#                 bid = int(round(0.25*self.value+0.75*min_bid))

#         return bid

#     def __repr__(self):
#         return "%s(id=%d, value=%d)" % (
#             self.__class__.__name__, self.id, self.value)