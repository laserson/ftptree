#! /usr/bin/env python

import os
import sys
import time
import json
import ftplib
import random
import logging
import datetime

# Object to access FTP site
class ftp_connection(object):
    def __init__(self, host, parser='mlsd'):
        self.host = host
        self.failed_attempts = 0
        self.max_attempts = 5
        self.connect()
        
        if callable(parser):
            self.list = parser
        elif parser == 'mlsd':
            self.list = self.list_mlsd
        elif parser == 'unix':
            self.list = self.list_unix
        elif parser == 'windows':
            self.list = self.list_windows
    
    def connect(self):
        self.ftp = ftplib.FTP(self.host, timeout=60)
        self.ftp.login()
        logging.info("CONNECT %s SUCCESS", self.host)
    
    # continually tries to reconnect ad infinitum
    def reconnect(self):
        try:
            self.ftp = ftplib.FTP(self.host, timeout=60)
            self.ftp.login()
            logging.warning("RECONNECT %s SUCCESS", self.host)
        except ftplib.all_errors:
            logging.warning("RECONNECT %s FAILED; trying again...", self.host)
            time.sleep(5 * random.uniform(0.5, 1.5))
            self.reconnect()
    
    # these functions interact with the FTP with no error checking
    # they just take a path and try to return properly-formatted data
    def list_mlsd(self, path):
        # copy of MLSD impl from Python 3.3 ftplib package that returns
        # listing data in a machine-readable format
        cmd = 'MLSD %s' % path
        lines = []
        self.ftp.retrlines(cmd, lines.append)
        results = []
        for line in lines:
            facts_found, _, name = line.rstrip('\r\n').partition(' ')
            entry = {}
            for fact in facts_found[:-1].split(";"):
                key, _, value = fact.partition("=")
                entry[key.lower()] = value
            results.append((name, entry))
        return results
    
    def list_windows(self, path):
        lines = []
        self.ftp.dir(path, lines.append)
        results = []
        for line in lines:
            fields = line.split()
            name = ' '.join(fields[3:])
            size = -1
            if fields[2].strip() == '<DIR>':
                type_ = 'dir'
            else:
                type_ = 'file'
                size = int(fields[2])
            results.append((name, {'type': type_, 'size': size}))
        return results
    
    def list_unix(self, path):
        lines = []
        self.ftp.dir(path, lines.append)
        results = []
        for line in lines:
            fields = line.split()
            name = ' '.join(fields[8:])
            size = -1
            if line[0] == 'd':
                type_ = 'dir'
            elif line[0] == '-':
                type_ = 'file'
                size = int(fields[4])
            elif line[0] == 'l':
                continue
            else:
                raise ValueError("Don't know what kind of file I have: %s" % line.strip())
            results.append((name, {'type': type_, 'size': size}))
        return results
    
    def test_methods(self):
        try:
            lines = []
            self.ftp.retrlines('MLSD', lines.append)
            print "MLSD SUCCESS"
            print '\n'.join(lines)
        except ftplib.all_errors:
            print "MLSD FAIL"
        
        lines = []
        self.ftp.retrlines('LIST', lines.append)
        print '\n'.join(lines)
        print "WINDOWS: name starts at 4th field; size/type is 3rd field"
        print "UNIX: type is first letter; size is 5th; name starts at 9th"
    
    # this function actually handles the logic of pulling data
    # it tries a max of max_attempts times
    def process_path(self, path):
        while self.failed_attempts < self.max_attempts:
            try:
                results = self.list(path)
                logging.info("LIST SUCCESS %s" % path)
                self.failed_attempts = 0
                return results
            except ftplib.all_errors:
                self.failed_attempts += 1
                logging.warning("LIST FAILED %s; Failed %i times out of %i; reconnecting...", path, self.failed_attempts, self.max_attempts)
                time.sleep(2 * random.uniform(0.5, 1.5))
                self.reconnect()
                continue
        
        # if I get here, I never succeeded in getting the data
        logging.warning("LIST ABANDONED %s", path)
        self.failed_attempts = 0
        return False
        

# Recursive building of FTP tree
def crawltree(ftp, tree):
    path = os.path.join(tree['ancestors'], tree['name'])
    results = ftp.process_path(path)
    if results == False:
        return tree
    
    for result in results:
        name = result[0]
        type_ = result[1]['type']
        if type_ == 'file':
            size = int(result[1]['size'])
            tree['children'][name] = {'name': name, 'ancestors': path, 'size': size, 'children': {}}
            logging.info("APPENDED file %s", os.path.join(path, name))
        elif type_ == 'dir':
            tree['children'][name] = crawltree(ftp, {'name': name, 'ancestors': path, 'size': -1, 'children': {}})
            logging.info("PROCESSED dir %s", os.path.join(path, name))
    
    return tree

# Traverse tree and compute sizes for internal nodes
def computesize(tree):
    if tree['size'] > -1:
        return tree['size']
    
    size = 0
    for child in tree['children'].itervalues():
        size += computesize(child)
    
    tree['size'] = size
    return size


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--output')
    parser.add_argument('--root', default='')
    parser.add_argument('--method', default='mlsd', help='One of "mlsd", "unix", or "windows".')
    parser.add_argument('--loglevel', default='INFO')
    parser.add_argument('--test-method', action='store_true')
    args = parser.parse_args()
    
    logging.basicConfig(filename=args.output+'.crawl.log',
                        filemode='w',
                        level=args.loglevel,
                        format="%(levelname)s|%(asctime)s|%(message)s")
    
    ftp = ftp_connection(args.host, args.method)
    
    if args.test_method == True:
        ftp.test_methods()
    else:
        tree = crawltree(ftp, {'name': '', 'ancestors': args.root.strip('/'), 'size': -1, 'children': {}})
        tree['date'] = str(datetime.date.today())
        weight = computesize(tree)
        logging.info("TOTAL WEIGHT %i bytes", weight)
        
        # dump json object
        with open(args.output, 'w') as op:
            json.dump(tree, op, encoding='ISO-8859-1')
