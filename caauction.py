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

from gsp import GSP
from vcg import VCG
from history import History
from stats import Stats

#from bbagent import BBAgent
#from truthfulagent import TruthfulAgent

from util import argmax_index, shuffled, mean, stddev

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





def init_agents(conf):
    """Each agent class must be already loaded, and have a
    constructor that takes an id, a value, and a budget, in that order."""
#    params = [(0, 10, conf.budget), (1, 20, conf.budget), (2, 30, conf.budget)]

#	This should look something like params = zip(range(n), value, demands)
    n = len(conf.agent_class_names)
    params = zip(range(n), conf.agent_values, itertools.repeat(conf.budget))
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

    # Need to have something here
    options.demands = ?
    options.capacities = ?

    logging.info("Starting simulation...")
    n = len(agents_to_run)

    totals = dict((id, 0) for id in range(n))
    total_revenues = []

    total_spent = [0 for i in range(n)]

    #Time to run the simulation
    logging.info("Time to Run the Simulation")

    total_rev = 0
    
    """ THIS IS WHERE WE HAVE A QUESTION - HOW DO WE REPRESENT INDIVIDUAL AGENT VALUES """
    options.agent_values = list(vals)
    values = dict(zip(range(n), list(vals)))
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