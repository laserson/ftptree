#! /usr/bin/env python

import json
import time
import logging
from itertools import izip
from subprocess import Popen

logging.basicConfig(format="%(asctime)s %(message)s")

with open('sites.json', 'r') as ip:
    sites = json.load(ip)

cmd = './crawltree.py --host %(host)s --root %(path)s --output %(treefile)s --method %(ftp_list_method)s'
processes = []
for site in sites:
    p = Popen(cmd % site, shell=True)
    processes.append(p)
    logging.info("INITIATED %s", site['id'])

try:
    finished = False
    while not finished:
        logging.info("SLEEPING")
        time.sleep(60)
        returncodes = [p.poll() for p in processes]
        for (c, p) in izip(returncodes, processes):
            if c is None:
                logging.info("CRAWLING %s", p['id'])
            elif c >= 0:
                logging.info("SUCCESS %s", p['id'])
            elif c < 0:
                logging.info("FAILED %s", p['id'])
        finished = all(returncodes)
except KeyboardInterrupt:
    logging.info("INTERRUPT")
    for p in processes:
        p.kill()
