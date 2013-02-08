import os
import sys
import time
import json
import ftplib

def log(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()

def connect(url):
    ftp = ftplib.FTP(url, timeout=60)
    ftp.login()
    return ftp

def is_file(line):
    return True if 'DIR' not in line else False

def is_dir(line):
    return not is_file(line)

def process_path(ftp, path):
    results = []
    ftp.dir(path, results.append)
    return results

def process_file(line):
    data = line.split()
    size = int(data[2])
    name = ' '.join(data[3:])
    return (name, size)

def process_dir(line):
    data = line.split()
    name = ' '.join(data[3:])
    return name

def crawl_tree(ftp, tree, debug=False):
    path = tree['name']
    
    if debug:
        log(path)    
    
    try:
        results = process_path(ftp, path)
    except ftplib.all_errors:
        log("# FTP time out; trying to reconnect")
        time.sleep(5)
        ftp = connect(url)
        results = process_path(ftp, path)
    
    for line in results:
        try:
            if is_file(line):
                (name, size) = process_file(line)
                tree['children'].append({'name': os.path.join(path, name), 'size': size})
                if debug:
                    log(os.path.join(path, name))
            elif is_dir(line):
                name = process_dir(line)
                tree['children'].append(crawl_tree(ftp, {'name': os.path.join(path, name), 'children': []}, debug))
        except ftplib.all_errors:
            log("Error with ftp command; skipping to next file")
    return tree

url = sys.argv[1]
ftp = connect(url)
tree = crawl_tree(ftp, {'name': '/', 'children': []}, True)
tree = crawl_tree(ftp, {'name': '/pub/Training', 'children': []}, True)
with open(sys.argv[2], 'w') as op:
    json.dump(tree, op, encoding='ISO-8859-1')
