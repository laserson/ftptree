#! /usr/bin/env python

import json
import time
import logging
from itertools import izip
from subprocess import Popen

logging.basicConfig(format="%(asctime)s %(message)s", level="INFO")

with open('sites.json', 'r') as ip:
    sites = json.load(ip)

processes = []
for site in sites:
    if site['path'] == '':
        cmd = './crawltree.py --host %(host)s --output %(treefile)s --method %(ftp_list_method)s'
    else:
        cmd = './crawltree.py --host %(host)s --root %(path)s --output %(treefile)s --method %(ftp_list_method)s'
    p = Popen(cmd % site, shell=True)
    processes.append(p)
    logging.info("INITIATED %s %s", site['id'], cmd % site)

try:
    finished = False
    while not finished:
        logging.info("SLEEPING")
        time.sleep(60)
        returncodes = [p.poll() for p in processes]
        for (c, s, p) in izip(returncodes, sites, processes):
            if c is None:
                logging.info("CRAWLING %s %s", s['id'], p.pid)
            elif c >= 0:
                logging.info("SUCCESS %s %s", s['id'], p.pid)
            elif c < 0:
                logging.info("FAILED %s %s", s['id'], p.pid)
        finished = all(returncodes)
except KeyboardInterrupt:
    logging.info("INTERRUPT")
    for (s, p) in izip(site, processes):
        p.kill()
        logging.info("KILLED %s %s", s['id'], p.pid)
