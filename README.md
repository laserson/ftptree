ftptree
=======

TL;DR
-----

Generate browsable tree map of FTP site weighted by the amount of data in each directory.

Components
----------

`crawltree.py`: takes an FTP URL and an output path and generates a JSON object
representing the FTP directory hierarchy along with the cumulative weight at
each node.
