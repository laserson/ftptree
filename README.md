ftptree
=======

Generate browsable tree map of FTP site weighted by the amount of data in each directory.

**Dependencies**

For the visualization, I use [d3.js](http://d3js.org/) along with [Bottle](http://bottlepy.org/).


**Components**

`crawltree.py`: takes an FTP URL and an output path and generates a JSON object
representing the FTP directory hierarchy along with the cumulative weight at
each node.  CAVEAT: the FTP site must implement the command `MLSD`.

**Crawled FTP sites**

* CDC: `./crawltree.py --url ftp.cdc.gov --output data/cdc.json --method windows`
* NCBI: `./crawltree.py --url ftp.ncbi.nih.gov --output data/ncbi.json --method mlsd`
