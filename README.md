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