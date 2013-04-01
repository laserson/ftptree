#! /usr/bin/env python

import os
import json

from bottle import Bottle, route, run, static_file, response

import squaripy
import crawltree

data_dir = 'data'

width = 960.
height = 600.

# preload data needed to render pages
# move this to a file eventually allow dropping new sites while server is running
sites = [{'id': 'cdc',
          'name': 'Centers for Disease Control and Prevention (CDC)',
          'host': 'ftp.cdc.gov',
          'root': '/',
          'treefile': 'cdc.json'},
         {'id': 'ncbi',
          'name': 'National Center for Biotechnology Information (NCBI)',
          'host': 'ftp.ncbi.nih.gov',
          'root': '/',
          'treefile': 'ncbi.json'}]

def load_cache():
    for site in sites:
    cache[site['host']] = {'meta': site}
    data_path = os.path.join(data_dir, site['treefile'])
    with open(data_path, 'r') as ip:
        tree = json.load(ip)
        cache[site['host']]['tree'] = tree

def is_cache_fresh():
    return True

cache = {}
load_cache()






def get_subtree(tree, path):
    # trim site-specific root
    path = path.strip('/')
    root = tree['__ancestors__'].strip('/')
    if root != '' and path.startswith(root):
        path = path[len(root):]
    path = path.strip('/')
    
    if path == '':
        return tree
    
    # traverse tree to get final object
    names = path.split('/')
    for name in names:
        tree = tree[name]
    
    return tree

def get_meta_object(tree):
    meta = {}
    for m in crawltree.iter_meta(tree):
        meta[m] = tree[m]
    return meta

def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)





app = Bottle()

@app.route('/')
def index():
    with open('index.html', 'r') as ip:
        return ''.join(ip.readlines())

@app.route('/refresh_cache')
def refresh_cache():
    if not is_cache_fresh():
        load_cache()

@app.route('/sites')
def site_list():
    response.content_type = 'application/json'
    return json.dumps(sites)

@app.route('/tree/<ftp_host>')
@app.route('/tree/<ftp_host>/')
@app.route('/tree/<ftp_host>/<path:path>')
def tree_layout(ftp_host, path=''):
    # get node metadata
    path = '/' + path
    subtree = get_subtree(cache[ftp_host]['tree'], path)
    children = [get_meta_object(subtree[child]) for child in iter_children(subtree)]
    sizes = [m['__size__'] for m in children]
    
    # sort the objects by size, descending
    order = argsort(sizes)[::-1]
    children = [children[i] for i in order]
    sizes = [sizes[i] for i in order]
    
    # compute the treemap layout
    rects = squaripy.squaripy(sizes, 0, 0, width, height)
    
    # merge the metadata with the layout data
    children = [d.update(r) for (d, r) in zip(children, rects)]
    
    data = get_meta_object(subtree)
    data['__children__'] = children
    
    return data

run(app, host='localhost', port=8080)
