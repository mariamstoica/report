# CA Auction Simulator
# Maria Stoica and Derek Booth
# CS 136 Final Project

from optparse import OptionParser
import copy
import itertools
import logging
import math
import pprint
import random
import sys

from caWDP import caWDP
from vcg import VCG
from history import History
from castats import CAStats

#from bbagent import BBAgent
#from truthfulagent import TruthfulAgent

from util import argmax_index, shuffled, mean, stddev

#Infinite string of zeros
zeros = itertools.repeat(0)

def sim(config):

	agents = init_agents(config)

	n = len(agents)
	by_id = dict((a.id, a) for a in agents)
	agent_ids = [a.id for a in agents]

	if (config.mechanism.lower() == 'cawdp'):
		mechanism = caWDP
	elif config.mechanism.lower() == 'vcg':
		mechanism = VCG
	else:
		raise ValueError("mechanism must be one of 'caWDP' or 'VCG'")

	allocation = {}
	payments = {}
	values = {}
	bids = {}

	history = History(bids, payments, allocation, n)

	def total_spent(agent_id, end):
		"""
        Compute total amount spent by agent_id through (not including)
        round end.
        """
		s = 0
		for t in range(end):
			agent_payment_t = filter(lambda p : p[0] == agent_id, payments[t])
			s += agent_payment_t[0][1]
		return s

	def run_round(t):

		# Get the bids from the agents
		if t == 0:
			bids[t] = [a.initial_bid() for a in agents]
		else:
			bids[t] = [a.bid(t, history) for a in agents]

		# Run the mechanism to determine allocation
		allocation[t] = mechanism.compute(config.capacities, bids[t])

		# Find the payment for each agent
		payments[t] = []
		for aid in agent_ids:
			agent_allocation = filter(lambda b : b[0] == aid, allocation[t])
			if len(agent_allocation) == 0:
				payments[t].append((aid,0))
			else:
				payments[t].append((aid, sum(b[2] for b in agent_allocation)))

		values[t] = dict(zip(agent_ids, zeros))

		def agent_value(agent_id, allocation, payments):
			agent_allocation = filter(lambda b : b[0] == agent_id, allocation)
			agent_value = 0
			if len(agent_allocation) > 0:
				for choice in agent_allocation:
					agent_value += sum([by_id[agent_id].values[i]*choice[1][i] for i in range(0, len(choice[1]))])
			agent_payment = filter(lambda p : p[0] == agent_id, payments)
			values[t][agent_id] = agent_value - agent_payment[0][1]
			return None

		map(lambda a : agent_value(a, allocation[t], payments[t]), agent_ids)

		log_console = False
		if log_console:
			logging.info("\t=== Round %d ===" % t)
			logging.info("\tbids: %s" % bids[t])
			logging.info("\tpayments: %s" % payments[t])
			logging.info("\tallocation: %s" % allocation[t])
			logging.info("\tUtility: %s" % values[t])
			logging.info("\ttotals spent: %s" % [total_spent(a.id, t+1) for a in agents])

	for t in range(0, config.num_rounds):
		run_round(t)

		for a in agents:
			history.set_agent_spent(a.id, total_spent(a.id, t))

	for a in agents:
		history.set_agent_spent(a.id, total_spent(a.id, config.num_rounds))

	return history

class Params:
	def __init__(self):
		self._init_keys = set(self.__dict__.keys())
    
	def add(self, k, v):
		self.__dict__[k] = v

	def __repr__(self):
		return "; ".join("%s=%s" % (k, str(self.__dict__[k])) for k in self.__dict__.keys() if k not in self._init_keys)

def init_agents(conf):
	"""Each agent class must be already loaded, and have a
	constructor that takes an id, a value, and a budget, in that order."""
	n = len(conf.agent_class_names)
	params = zip(range(n), conf.agent_values, conf.agent_demands)
	def load(class_name, params):
		agent_class = conf.agent_classes[class_name]
		return agent_class(*params)

	return map(load, conf.agent_class_names, params)

def configure_logging(loglevel):
	numeric_level = getattr(logging, loglevel.upper(), None)
	if not isinstance(numeric_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)

	root_logger = logging.getLogger('')
	strm_out = logging.StreamHandler(sys.__stdout__)
	strm_out.setFormatter(logging.Formatter('%(message)s'))
	root_logger.setLevel(numeric_level)
	root_logger.addHandler(strm_out)

def load_modules(agent_classes):
	"""Each agent class must be in module class_name.lower().
	Returns a dictionary class_name->class"""

	def load(class_name):
		module_name = class_name.lower()  # by convention / fiat
		module = __import__(module_name)
		agent_class = module.__dict__[class_name]
		return (class_name, agent_class)

	return dict(map(load, agent_classes))

def parse_agents(args):
	"""
	Each element is a class name like "Peer", with an optional
	count appended after a comma.  So either "Peer", or "Peer,3".
	Returns an array with a list of class names, each repeated the
	specified number of times.
	"""
	ans = []
	for c in args:
		s = c.split(',')
		if len(s) == 1:
			ans.extend(s)
		elif len(s) == 2:
			name, count = s
			ans.extend([name]*int(count))
		else:
			raise ValueError("Bad argument: %s\n" % c)
	return ans

def main(args):

	usage_msg = "Usage: %prog [options] Bidder1[,cnt] Bidder2[,cnt] ..."
	parser = OptionParser(usage=usage_msg)

	def usage(msg):
		print "Error: %s\n" % msg
		parser.print_help()
		sys.exit()

	parser.add_option("--loglevel",
                      dest="loglevel", default="info",
                      help="Set the logging level: 'debug' or 'info'")

	parser.add_option("--mech",
                      dest="mechanism", default="caWDP",
                      help="Set the mechanim: 'caWDP' or 'vcg'")

	parser.add_option("--num-rounds",
                      dest="num_rounds", default=48, type="int",
                      help="Set number of rounds")
    
    #parser.add_option("--reserve",
    #                  dest="reserve", default=0, type="int",
    #                  help="Reserve price, in cents")

	#parser.add_option("--iters",
	#                 dest="iters", default=1, type="int",
	#                 help="Number of different value draws to sample. Set to 1 for debugging.")

	#parser.add_option("--seed",
	#                 dest="seed", default=None, type="int",
	#                 help="seed for random numbers")

	(options, args) = parser.parse_args()

	#leftover agents are class names

	if len(args) == 0:
		#default
		agents_to_run = ['Truthful', 'Truthful', 'Truthful']
	else:
		agents_to_run = parse_agents(args)

	configure_logging(options.loglevel)

    # Add some more config options
	options.agent_class_names = agents_to_run
	options.agent_classes = load_modules(options.agent_class_names)

	logging.info("Starting simulation...")
	n = len(agents_to_run)

	totals = dict((id, 0) for id in range(n))
	total_revenues = []

	total_spent = [0 for i in range(n)]

    #Time to run the simulation
	logging.info("Time to Run the Simulation")

	total_rev = 0

    # Choose the demands, capacities, and values for each agent
	options.agent_demands = [[2,3,2] for i in range(0, n)]
	options.capacities = [20,27,20]
	options.agent_values = []

	for i in range(0, n):
		options.agent_values.append([random.randint(3,6), random.randint(5,8), random.randint(6,11)])
    
	""" Decide the agent values """
	values = dict(zip(range(n), options.agent_values))
    ##   Runs simulation  ###
	history = sim(options)
    ###  simulation ends.
	stats = CAStats(history, values)
    # Print stats in console?
    # logging.info(stats)
    
	for id in range(n):
		totals[id] += stats.total_utility(id)
		total_spent[id] += history.agents_spent[id]
	total_rev += stats.total_revenue()

    #total_revenues.append(total_rev / float(num_perms))

    # Averages are over all the value permutations considered    
	logging.info("%s\t\t%s\t\t%s" % ("#" * 15, "RESULTS", "#" * 15))
	logging.info("")
	for a in range(n):
		logging.info("Stats for Agent %d, %s" % (a, agents_to_run[a]) )
		logging.info("Average spend $%.2f" % (total_spent[a]/float(options.num_rounds)))   
		logging.info("Average utility  $%.2f" % (totals[a]/float(options.num_rounds)))
		logging.info("-" * 40)
		logging.info("\n")
	logging.info("Total revenue $%.2f" % (total_rev))
#print "config", config.budget
    
    #for t in range(47, 48):
    #for a in agents:
        #print a,"'s added values is", av_value[a.id]
        
if __name__ == "__main__":
	main(sys.argv)