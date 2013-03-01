#! /usr/bin/env python

import os
import sys
import time
import json
import ftplib
import datetime

def log(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()

# Object to access FTP site
class ftp_connection(object):
    def __init__(self, url, parser='mlsd'):
        self.url = url
        self.failed_attempts = 0
        self.max_attempts = 5
        self.reconnect()
        
        if callable(parser):
            self.list = parser
        elif parser == 'mlsd':
            self.list = self.list_mlsd
        elif parser == 'unix':
            self.list = self.list_unix
        elif parser == 'windows':
            self.list = self.list_windows
    
    # continually tries to reconnect ad infinitum
    def reconnect(self):
        try:
            self.ftp = ftplib.FTP(self.url, timeout=60)
            self.ftp.login()
            log("Successfully reconnected to %s" % self.url)
        except ftplib.all_errors:
            log("Failed to reconnect to %s; trying again..." % self.url)
            time.sleep(5)
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
            if line[0] == 'd':
                type_ = 'dir'
            elif line[0] == '-':
                type_ = 'file'
                size = int(fields[4])
            results.append((name, {'type': type_, 'size': size}))
        return results
    
    def test_methods(self):
        try:
            lines = []
            ftp.ftp.retrlines('MLSD', lines.append)
            log("MLSD SUCCESS")
            log('\n'.join(lines))
        except ftplib.all_errors:
            log("MLSD FAIL")
        
        lines = []
        ftp.ftp.retrlines('LIST', lines.append)
        log('\n'.join(lines))
        
        log("WINDOWS: name starts at 4th field; size/type is 3rd field")
        log("UNIX: type is first letter; size is 5th; name starts at 9th")
    
    # this function actually handles the logic of pulling data
    # it tries a max of max_attempts times
    def process_path(self, path):
        while self.failed_attempts < self.max_attempts:
            try:
                results = self.list(path)
                log("Processed %s" % path)
                return results
            except ftplib.all_errors:
                self.failed_attempts += 1
                log("Failed %i times on %s; trying to reconnect..." % (self.failed_attempts,path))
                time.sleep(2 * random.uniform(0.5, 1.5))
                continue
        
        # if I get here, I never succeeded in getting the data
        return False
        

# Recursive building of FTP tree
def crawltree(ftp, tree):
    path = tree['name']
    results = ftp.process_path(path)
    if results == False:
        return tree
    
    for result in results:
        name = result[0]
        type_ = result[1]['type']
        if type_ == 'file':
            size = int(result[1]['size'])
            tree['children'].append({'name': os.path.join(path, name), 'size': size, 'children': []})
            log("Appended file %s" % os.path.join(path, name))
        elif type_ == 'dir':
            tree['children'].append(crawltree(ftp, {'name': os.path.join(path, name), 'size': -1, 'children': []}))
    
    return tree

# traverse tree and compute sizes for internal nodes
def computesize(tree):
    if tree['size'] > -1:
        return tree['size']
    
    size = 0
    for child in tree['children']:
        size += computesize(child)
    
    tree['size'] = size
    return size

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--output')
    parser.add_argument('--method', default='mlsd', help='One of "mlsd", "unix", or "windows".')
    parser.add_argument('--test-method', action='store_true')
    args = parser.parse_args()
    
    ftp = ftp_connection(args.url, args.method)
    
    if args.test_method == True:
        ftp.test_methods()
    else:
        tree = crawltree(ftp, {'name': '/', 'size': -1, 'children': []})
        tree['date'] = str(datetime.date.today())
        weight = computesize(tree)
        log("Total weight in tree is %i" % weight)
        
        # dump json object
        with open(args.output, 'w') as op:
            json.dump(tree, op, encoding='ISO-8859-1')
