#!/usr/bin/env python

import sys

class FixedPM:
    """Truthful bidding"""
    def __init__(self, id, values, demands):
        self.id = id
        self.values = values
        self.demands = demands
        self.bundle_value = sum([self.values[i]*self.demands[i] for i in range(0, len(self.values))])
        self.pm = .2

    def initial_bid(self):
        return (self.id, self.demands, (1-self.pm)*self.bundle_value)

    def bid(self, t, history):
        return self.initial_bid()