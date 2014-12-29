FTPTREE
=======

Generates browsable tree map of an FTP site weighted by the amount of data in
each directory. FTP site is crawled using `scrapy`.


Installation
------------

Requires `python>=2.7`.

Required python modules:

* `scrapy` for crawling FTP sites

* `squarify` for laying out tree maps

* `bottle` for lightweight web server

Modules used for visualization/front end:

* d3.js

* Twitter Bootstrap

* jQuery

Clone package from GitHub, e.g.,

    git clone git://github.com/laserson/ftptree.git

The web app is run directly from the root project directory using `servetree.py`.


Usage overview
--------------

`sites.json` contains a JSON list of FTP site metadata objects describing which
sites to include in the visualization.

`crawltree.py` crawls an FTP site and generates a JSON object representation of
the directory tree, including sizes of the files.

`crawlsites.py` is a script to crawl each site listed in `sites.json`.

`servetree.py` is the Bottle.py app that serves the visualization.

The `static/` directory contains the Bootstrap files.

`index.html` is the main d3.js visualization.

To crawl:

```bash
scrapy crawl ftptree -a config_file=sites/ncbi.json -s JOBDIR=tmp_crawl/ncbi -o crawls/ncbi.txt -t jsonlines
scrapy crawl ftptree -a config_file=sites/ucsc.json -s JOBDIR=tmp_crawl/ucsc -o crawls/ucsc.txt -t jsonlines
scrapy crawl ftptree -a config_file=sites/cdc.json -s JOBDIR=tmp_crawl/cdc -o crawls/cdc.txt -t jsonlines
```


How to crawl an FTP tree
------------------------

The `crawltree.py` script parses results from an FTP `LIST` command.  The
results differ based on the server properties.  Primarily, the data format can
be "unix", "windows", or "mlsd".  The `MLSD` command is preferred as it returns
pre-parsed file information.

To determine the method to use for a given FTP site, run e.g.

    ./crawltree.py --host ftp.cdc.gov --output data/cdc.json --test-method

which will return a sample listing.  It will specify whether `MLSD` succeeded or
failed.  If failed, it will show an example listing so the user can determine
whether it's Unix-like or Windows-like.

After the appropriate listing method is determined, a typical crawling command
is issued like so:

    ./crawltree.py --host ftp.cdc.gov --output data/cdc.json --method windows

You can specify where to start the crawl by adding a `--root path/to/root`
option, e.g.,

    ./crawltree.py --host hgdownload.cse.ucsc.edu --root goldenPath --output data/ucscgb.json --method mlsd




OLD OLD OLD
===========

**Crawled FTP sites**

* CDC: `./crawltree.py --host ftp.cdc.gov --output data/cdc.json --method windows`
* NCBI: `./crawltree.py --host ftp.ncbi.nih.gov --output data/ncbi.json --method mlsd`
* 1kg: `./crawltree.py --host ftp-trace.ncbi.nih.gov --root 1000genomes/ftp --output data/1kg.json --method mlsd`

* Genome Browser: `./crawltree.py --host hgdownload.cse.ucsc.edu --root goldenPath --output data/ucscgb.json --method mlsd`

ftp://ftp.ncbi.nlm.nih.gov/sra

ftp://ftp.fcc.gov/
ftp://ftp.rma.usda.gov/pub/
ftp://ftp.epa.gov/
ftp://ftp.fsa.usda.gov/
ftp://ftp.ngdc.noaa.gov/
ftp://tgftp.nws.noaa.gov/
ftp://ftp.ncdc.noaa.gov/pub
ftp://ftp.cdc.noaa.gov/
ftp://ftp2.census.gov
ftp://emi.nasdaq.com/
ftp://ftp.nasdaqtrader.com/
ftp://ftp.resource.org/
ftp://ftp.uspto.gov/pub/
ftp://ftp.eia.doe.gov/
ftp://ftp.broadinstitute.org/pub
ftp://ftpext.usgs.gov/pub/