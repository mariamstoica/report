# needs to get bids, capacities

import random

class WDP:
	""" Given the capacities of each resource and the bids on
	the resources, this computes the winning set of bids 
	and the prices each agent makes """

	""" Each bid looks like (id_i, [s_1, ..., s_m], p_i), where s_i are 
	the amounts of each resource he is willing to bid for and 
	p_i is the price of this bid """

	""" We assume the bids are valid, in that each 0 <= s_i <= d_i
	for the demand limits d_i on each resource """

	@staticmethod
	def compute(capacities, bids):
		
		""" Start by defining a function which checks for us if a bid
		is allowable based on the capacities """
		def allowable(bid_list, capacities):
			total = [0 for i in range(0, len(capacities))]
			for i in range(0, len(total)):
				for b in bid_list:
					total[i] += b[1][i]

			check = True
			for i in range(0, len(capacities)):
				if total[i] > capacities[i]:
					check = False

			return check

		""" Basic idea - all the single bids will be valid, so we first 
		test if any pairs work.  Then test triples, etc.  Max of 3 checks
		(for now) since only 3 agents """

		allocation = max(bids, key = lambda b : b[2])
		revenue = allocation[2]

		""" Now, if there are possible allowable pairs of bids, we pick the
		best option """

		pair1 = [bids[0], bids[1]]
		pair2 = [bids[0], bids[2]]
		pair3 = [bids[1], bids[2]]

		allowable_pairs = filter(lambda a : allowable(a, capacities), [pair1, pair2, pair3])

		random.shuffle(allowable_pairs)

		prices = [(0,0) for i in range(0, len(allowable_pairs))]
		for i in range(0, len(allowable_pairs)):
			prices[i] = (allowable_pairs[i][0][2] + allowable_pairs[i][1][2], i)

		best_price = max(prices, key = lambda p : p[0])

		best_pair = allowable_pairs[best_pair[1]]

		# Break ties in favor of giving to more people
		if best_price[0] >= revenue:
			allocation = best_pair
			revenue = best_price[0]

		""" Finally, we check the triple """
		if (allowable(bids, capacities)):
			triple_price = sum(b[2] for b in bids)

			if triple_price >= revenue:
				allocation = bids
				revenue = triple_price

		return allocation