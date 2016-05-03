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
		self.rho = 5
		self.s = [0,.05]
		self.a = set([-.1, .1])
		self.step_history = [.1]
		self.step = .1
		self.cutoff = .01
		self.lamb = 10
		self.phi = 7
		self.gamma = 1.4
		self.r = 0
		self.Q_values = {(.05, .1): .1}
		self.v = {}
		self.alpha = 0.2
		self.beta = 0.1
		self.old_s = 0
		self.old_a = 0
		# self.psi = 3
		# self.chi = 3
		# self.delta = 1
		# self.utility = 0
		# self.profit_margin_history_center = 0
		# self.reset_lower = 0
		# self.reset_higher = 0

	def initial_bid(self):
		return (self.id, self.demands, (1-self.s[-1])*self.bundle_value)

	def bid(self, t, history):
		# def decrease_step():
		# 	most_recent_pms = self.pm[-self.lamb:]
		# 	mean = np.mean(most_recent_pms)
		# 	omegas = [0 for i in range(0, len(most_recent_pms))]
		# 	for i in range(0, len(most_recent_pms)):
		# 		if abs(most_recent_pms[i]-mean) <= self.step:
		# 			omegas[i] = 1
		# 	if sum(omegas) >= self.phi and omegas[-1] == 1 and ((self.s[-1] < mean and self.delta == 1) or (self.s[-1] >= mean and self.delta == -1)):
		# 		self.step = self.step / float(self.gamma)
		# 		self.profit_margin_history_center = mean

		# def profit_margin_reset():
		# 	d = self.pm[-1] - self.profit_margin_history_center
		# 	if abs(d) > self.psi * self.step:
		# 		if d > 0:
		# 			self.reset_lower = 0
		# 			self.reset_higher += 1
		# 			if self.reset_higher < self.chi:
		# 				self.pm[-1] = self.profit_margin_history_center
		# 			else:
		# 				self.profit_margin_history_center = self.pm[-1]
		# 				self.reset_higher = 0
		# 		else:
		# 			self.reset_higher = 0
		# 			self.reset_lower += 1
		# 			if self.reset_lower < self.chi:
		# 				self.pm[-1] = self.profit_margin_history_center
		# 			else:
		# 				self.profit_margin_history_center = self.pm[-1]
		# 				self.reset_lower = 0

		def compute_r(s, a, bidding_history):
			s_star = s+a
			frac = sum(b[4] for b in bidding_history)/float(sum(b[3]+b[4] for b in bidding_history))
			return s_star*frac

		def compute_q(s, a, r_val, old):
			if self.v[(s,a)] == 0:
				return r_val
			else:
				Q_value_pairs = self.Q_values.keys()
				if old:
					theta_close = filter(lambda pair : abs(pair[0] - s) < self.theta, Q_value_pairs)
				else:
					theta_close = filter(lambda pair : abs(pair[0] - (s+a)) < self.theta, Q_value_pairs)
				a_values = list(set(map(lambda pair : pair[1], theta_close)))
				m = []
				for a_val in a_values:
					this_a = filter(lambda pair : pair[1] == a_val, theta_close)
					m.append(np.mean(this_a))
				M = max(m)
				return (1-self.alpha)*self.Q_values[(s,a)] + self.alpha*[r_val + self.beta*M]

		def decrease_theta():
			most_recent_s = self.s[-self.lamb:]
			mean = np.mean(most_recent_s)
			omegas = [0 for i in range(0, len(most_recent_s))]
			for i in range(0, len(most_recent_s)):
				if abs(most_recent_pms[i]-mean) <= self.step_history[i]:
					omegas[i] = 1
			if sum(omegas) >= self.phi and omegas[-1] == 1 and ((self.s[-1] < mean and self.delta == 1) or (self.s[-1] >= mean and self.delta == -1)):
				return True
			return False

		def fillQValues():
			for pm in self.s:
				for aval in self.a:
					if (pm, aval) not in self.v.keys():
						L = filter(lambda pair : abs(pair[0] - (pm + aval)) < self.step, self.Q_values,keys())
						if len(L) > 0:
							self.Q_values[(pm, aval)] = np.mean(L)
							self.v[(pm, aval)] = 1

		prev_round = history.round(t-1)
		win = 0
		agent_winner = filter(lambda a : a[0] == self.id, prev_round.payments)
		if len(agent_winner) > 0:
			win = 1
		else:
			self.wait += 1

		self.bidding_history.append((self.demands, self.bundle_value, self.s[-1], self.wait, win))

		if self.wait >= self.tau:
			self.bidding_history = []
			self.pm.append(min(0, self.pm - self.step))

		elif len(self.bidding_history) >= self.rho and self.step > self.cutoff:
			current_reward = compute_r(self.s[-2], self.s[-1]-self.s[-2], self.bidding_history)

			self.old_s = self.s[-1]

			self.Q_values[(self.old_s, self.s[-1]-self.s[-2])] = compute_q(self.old_s, self.s[-1]-self.s[-2], current_reward, True)
			if (self.old_s, self.s[-1] - self.s[-2]) in self.v.keys():
				self.v[(self.old_s, self.s[-1]-self.s[-2])] += 1
			else:
				self.v[(self.old_s, self.s[-1]-self.s[-2])] = 1

			q = compute_q(self.s[-1], self.s[-1]-self.s[-2], current_reward, False)
			self.Q_values[(self.s[-1], self.s[-1]-self.s[-2])] = q

			if decrease_theta():
				self.step = self.step/float(self.gamma)
				if self.step not in self.a:
					self.a.add(self.step)
					self.a.add(-self.step)

			if ((self.old_s, self.step) in self.v.keys()) and ((self.old_s, -self.step) in self.v.keys()):
				q1 = self.Q_values[(self.old_s, self.step)]
				q2 = self.Q_values[(self.old_s, -self.step)]
				if q1 > q_2:
					a = self.step
				else:
					a = -self.step
			else if ((self.old_s, self.step) not in self.v.keys()) and ((self.old_s, -self.step) not in self.v.keys()):
				q1 = 0
				q2 = 0
				if (self.old_s, self.step*self.gamma) in self.v.keys():
					q1 = self.Q_values[(self.old_s, self.step*self.gamma)]
				if (self.old_s, -self.step*self.gamma) in self.v.keys():
					q2 = self.Q_values[(self.old_s, -self.step*self.gamma)]

				if q1 > q2:
					a = self.step
				else:
					a = -self.step
			else:
				if self.r >= current_reward:
					a = self.old_a
				else:
					a = -self.old_a

			s = self.old_s + a
			self.old_r = current_reward
			self.old_s = s
			self.s.append(s)
			self.step_history.append(self.step)
			self.old_a = a

			fillQValues()

			# u_expected = self.pm[-1] * sum(h[4] for h in self.bidding_history)/float(sum(h[3]+h[4] for h in self.bidding_history))
			# decrease_step()

			# if u_expected < self.utility:
			# 	self.pm.append(self.pm[-1] - self.delta*self.step)
			# else:
			# 	self.pm.append(self.pm[-1] + self.delta*self.step)

			# if self.pm[-1] > self.pm[-2]:
			# 	self.delta = 1
			# elif self.pm[-1] < self.pm[-2]:
			# 	self.delta = -1

			# self.utility = u_expected

			# profit_margin_reset()

		return (self.id, self.demands, (1-self.s[-1])*self.bundle_value)