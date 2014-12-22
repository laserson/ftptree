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
class FTPConnection(object):
    def __init__(self, host, parser=None):
        self.host = host
        self.failed_attempts = 0
        self.max_attempts = 5
        self.stop_when_connected()
        
        if parser is None:
            # try to guess on first access
            logging.info("No parser provided; will guess on first attempt.")
            self._listfn = None
        elif callable(parser):
            # supply a custom listing parser
            logging.info("Supplied a custom dir listing parser.")
            self._listfn = parser
        elif parser == 'mlsd':
            logging.info("Set parser to MLSD.")
            self._listfn = self._list_mlsd
        elif parser == 'unix':
            logging.info("Set parser to UNIX.")
            self._listfn = self._list_unix
        elif parser == 'windows':
            logging.info("Set parser to WINDOWS.")
            self._listfn = self._list_windows
    
    def _connect(self):
        # attempt an anonymous FTP connection
        logging.info("CONNECT %s ATTEMPT", self.host)
        self.ftp = ftplib.FTP(self.host, timeout=60)
        self.ftp.login()
        logging.info("CONNECT %s SUCCESS", self.host)
    
    def stop_when_connected(self):
        # continually tries to reconnect ad infinitum
        try:
            self._connect()
        except ftplib.all_errors:
            logging.warning("CONNECT %s FAILED; trying again...", self.host)
            time.sleep(5 * random.uniform(0.5, 1.5))
            self.stop_when_connected()
    
    def _list(self, path):
        # public fn to get a path listing
        # guesses the format if it's not explicitly set
        try:
            return self._listfn(path)
        except AttributeError:
            # self._listfn is not defined;
            # try to guess it
            self._listfn = self._guess_parser(path)
            return self._listfn(path)
    
    def _guess_parser(self, path):
        # also check out this library: http://cr.yp.to/ftpparse.html
        logging.info("Guessing FTP listing parser for %s...", self.host)
        try:
            lines = []
            self.ftp.retrlines('MLSD %s' % path, lines.append)
            logging.info("Guessing parser: MLSD success")
            return self._list_mlsd
        except ftplib.all_errors:
            logging.info("Guessing parser: MLSD fail")
        
        # not MLSD, so:
        # get a listing and check a few properties
        dir_in_3rd = lambda line: "<DIR>" in line.split()[2]
        numeric_first_letter = lambda line: line[0] >= '0' and line[0] <= '9'
        unix_first_letter = lambda line: line[0] in 'd-lpsbc'
        
        lines = []
        self.ftp.retrlines('LIST %s' % path, lines.append)
        
        # check for windows
        if (any(map(dir_in_3rd, lines)) and
                all(map(numeric_first_letter, lines))):
            logging.info("Guessing parser: WINDOWS")
            return self._list_windows
        
        # check for unix
        if all(map(unix_first_letter, lines)):
            logging.info("Guessing parser: UNIX")
            return self._list_unix
        
        logging.error('\n'.join(lines))
        raise RuntimeError("Failed to guess parser.")
    
    # these functions interact with the FTP with no error checking
    # they just take a path and try to return properly-formatted data
    def _list_mlsd(self, path):
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
    
    def _list_windows(self, path):
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
    
    def _list_unix(self, path):
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
    
    # this function actually handles the logic of pulling data
    # it tries a max of max_attempts times
    def process_path(self, path):
        while self.failed_attempts < self.max_attempts:
            try:
                results = self._list(path)
                logging.info("LIST SUCCESS %s" % path)
                self.failed_attempts = 0
                return results
            except ftplib.all_errors:
                self.failed_attempts += 1
                self.ftp.close()
                logging.warning("LIST FAILED %s; Failed %i times out of %i; reconnecting...", path, self.failed_attempts, self.max_attempts)
                time.sleep(2 * random.uniform(0.5, 1.5))
                self.stop_when_connected()
        
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
    parser.add_argument('config')
    parser.add_argument('--loglevel', default='INFO')
    args = parser.parse_args()
    
    with open(args.config, 'r') as ip:
        config = json.loads(ip.read())
    
    logging.basicConfig(filename=config['id'] + '.crawl.log',
                        filemode='w',
                        level=args.loglevel,
                        format="%(levelname)s|%(asctime)s|%(message)s")
    
    ftp = FTPConnection(config['host'], config['ftp_list_method'])    
    tree = crawltree(ftp, {'name': '', 'ancestors': config['root_path'].strip('/'), 'size': -1, 'children': {}})
    tree['date'] = str(datetime.date.today())
    weight = computesize(tree)
    logging.info("TOTAL WEIGHT %i bytes", weight)
    
    # dump json object
    with open(config['tree_file'], 'w') as op:
        json.dump(tree, op, encoding='ISO-8859-1')
