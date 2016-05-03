#!/usr/bin/env python

import sys

import numpy as np

class QLearn:
	"""Truthful bidding"""
	def __init__(self, id, values, demands):
		self.id = id
		self.values = values
		self.demands = demands
        
		# Value for this bundle
		self.bundle_value = sum([self.values[i]*self.demands[i] for i in range(0, len(self.values))])

		# Descriptions of previous bids
		self.bidding_history = []
		self.wait = 0

		# Parameters for the bidding strategy
		self.tau = 3
		self.kappa = 5
		self.pm = [.05]
		self.step = .1
		self.cutoff = .01
		self.lamb = 10
		self.phi = 6
		self.gamma = 2
		self.psi = 3
		self.chi = 3
		self.delta = 1
		self.utility = 0
		self.profit_margin_history_center = 0
		self.reset_lower = 0
		self.reset_higher = 0

	def initial_bid(self):
		return (self.id, self.demands, (1-self.pm[-1])*self.bundle_value)

	def bid(self, t, history):
		prev_round = history.round(t-1)
	    
		def decrease_step():
			most_recent_pms = self.pm[-self.lamb:]
			mean = np.mean(most_recent_pms)
			omegas = [0 for i in range(0, len(most_recent_pms))]
			for i in range(0, len(most_recent_pms)):
				if abs(most_recent_pms[i]-mean) <= self.step:
					omegas[i] = 1
			if sum(omegas) >= self.phi and omegas[-1] == 1 and ((self.pm[-1] < mean and self.delta == 1) or (self.pm[-1] >= mean and self.delta == -1)):
				self.step = self.step / float(self.gamma)
				self.profit_margin_history_center = mean

		def profit_margin_reset():
			d = self.pm[-1] - self.profit_margin_history_center
			if abs(d) > self.psi * self.step:
				if d > 0:
					self.reset_lower = 0
					self.reset_higher += 1
					if self.reset_higher < self.chi:
						self.pm[-1] = self.profit_margin_history_center
					else:
						self.profit_margin_history_center = self.pm[-1]
						self.reset_higher = 0
				else:
					self.reset_higher = 0
					self.reset_lower += 1
					if self.reset_lower < self.chi:
						self.pm[-1] = self.profit_margin_history_center
					else:
						self.profit_margin_history_center = self.pm[-1]
						self.reset_lower = 0

		win = 0
		agent_winner = filter(lambda a : a[0] == self.id, prev_round.payments)
		if len(agent_winner) > 0:
			win = 1
		else:
			self.lose += 1

		self.bidding_history.append((self.demands, self.bundle_value, self.pm, self.lose, win))

		if self.lose >= self.tau:
			self.bidding_history = []
			self.pm.append(min(0, self.pm - self.step))

		elif len(self.bidding_history) >= self.kappa and self.step > self.cutoff:
			u_expected = self.pm[-1] * sum(h[4] for h in self.bidding_history)/float(sum(h[3]+h[4] for h in self.bidding_history))
			decrease_step()

			if u_expected < self.utility:
				self.pm.append(self.pm[-1] - self.delta*self.step)
			else:
				self.pm.append(self.pm[-1] + self.delta*self.step)

			if self.pm[-1] > self.pm[-2]:
				self.delta = 1
			elif self.pm[-1] < self.pm[-2]:
				self.delta = -1

			self.utility = u_expected

			profit_margin_reset()

		return (self.id, self.demands, (1-self.pm[-1])*self.bundle_value)