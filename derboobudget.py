#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index

class DerBoobudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2

    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        #The expected utilities will be calculated in the same way, since
        #the final ranking will be based on these utility value calculations

        #From the history, find the click values and other bids
        prev_round = history.round(t-1)
        clicks = prev_round.clicks
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        #Sort other_bids by bid value

        other_bids.sort(key=lambda bid: bid[1], reverse=True)

        #The utility of position j (0-indexed) is the click value
        #clicks[j] * (value minus other_bid[j]), as we are finding the
        #expected utility of beating that bid, meaning we'd have
        #to pay the amount of that bid.  Also, the number of positions
        #is one less than the number of bids, so it is the length of the
        #other_bids array

        num_positions = len(other_bids)

        utilities = []
        for i in range(0, num_positions):
            utilities.append(clicks[i]*(self.value-other_bids[i][1]))

        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        # For the first 16 rounds, we simply bid 35 to raise the minimum
        # price of an allocation (likely, these will be hotly contested places,
        # so we will never actually purchase anything at this price.
        if t < 16:
            bid = 35

        # For the middle rounds, with 16 <= t < 33, we underbid the
        # balanced bidding value, so that we can have a chance at taking some
        # undervalued positions at low prices.

        if t >= 16 and t < 33:
            if min_bid >= self.value:
                bid = self.value

            elif slot == 0:
                bid = int(round(0.6*self.value))

            else:
                bid = int(round(0.1*self.value+0.9*min_bid))

        # Otherwise, starting at period 32, we overbid the balanced bidding value
        # to quickly use up the rest of our budget on high-value places.  I feel
        # like people will prioritize periods at the very start or at the very end,
        # so starting this high-value bidding slightly early may give a chance at
        # additional value before prices skyrocket towards the end of the round.

        else:

            # If the min_bid is greater than or equal to the value at this position,
            # just bid the value to the bidder.

            if min_bid >= self.value:
                bid = self.value

            # Otherwise, if the position we're aiming for is first place, bid slightly
            # more than our value
            elif slot == 0:
                bid = int(round(1.1*self.value))

            # Finally, if we are somewhere in the middle, overbid the balanced bidding
            # value.

            else:
                bid = int(round(0.6*self.value+0.4*min_bid))

        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


