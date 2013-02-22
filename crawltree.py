#! /usr/bin/env python

import os
import sys
import time
import json
import ftplib

def log(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()

# Object to access FTP site
class ftp_connection(object):
    def __init__(self, url):
        self.url = url
        self.reconnect()
    
    def reconnect(self):
        try:
            self.ftp = ftplib.FTP(self.url, timeout=60)
            self.ftp.login()
            log("Successfully reconnected to %s" % self.url)
        except ftplib.all_errors:
            log("Failed to reconnect to %s; trying again..." % self.url)
            self.reconnect()
    
    def process_path(self, path):
        try:
            results = []
            self.ftp.dir(path, results.append)
            log("Processed %s" % path)
            return results
        except ftplib.all_errors:
            log("Failed on %s; trying to reconnect..." % path)
            time.sleep(5)
            self.reconnect()
            return self.process_path(path)


# Functions to parse data returned by FTP commands
def is_file(line):
    return True if 'DIR' not in line else False

def is_dir(line):
    return not is_file(line)

def process_file(line):
    data = line.split()
    size = int(data[2])
    name = ' '.join(data[3:])
    return (name, size)

def process_dir(line):
    data = line.split()
    name = ' '.join(data[3:])
    return name

# Recursive building of FTP tree
def crawltree(ftp, tree):
    path = tree['name']
    results = process_path(ftp, path)
    for line in results:
        if is_file(line):
            (name, size) = process_file(line)
            tree['children'].append({'name': os.path.join(path, name), 'size': size, 'children': []})
            log("Appended file %s" % os.path.join(path, name))
        elif is_dir(line):
            name = process_dir(line)
            tree['children'].append(crawltree(ftp, {'name': os.path.join(path, name), 'size': -1, 'children': []}))
    return tree

def computesize(tree):
    if tree['size'] > -1:
        return tree['size']
    
    size = 0
    for child in tree['children']:
        size += computesize(child)
    
    tree['size'] = size
    return size

# main script here:
url = sys.argv[1]
ftp = ftp_connection(url)
tree = crawltree(ftp, {'name': '/', 'size': -1, 'children': []})
log("Total weight in tree is %i" % computesize(tree))

# dump json object
with open(sys.argv[2], 'w') as op:
    json.dump(tree, op, encoding='ISO-8859-1')
