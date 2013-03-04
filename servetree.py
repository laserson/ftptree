from bottle import Bottle, route, run

# TREEMAP LAYOUT CODE
# Impl from Bruls, Huizing, van Wijk, "Squarified Treemaps"
# Corrected here: http://stackoverflow.com/questions/9880635/implementing-a-squarified-treemap-in-javascript

def worst(R, w):
    s = sum(R)
    v1 = (w ** 2) * max(r) / (s ** 2)
    v2 = (s ** 2) / (min(r) / (w ** 2))
    return max(v1, v2)

def squarify(children, row, w):
    c = children[0]
    if len(row) == 0 or worst(row, w) >= worst([c] + row, w):
        remaining = children[1:]
        if len(remaining) == 0:
            layoutrow([c] + row)
        else:
            squarify(remaining, [c] + row, w)
    else:
        layoutrow(row)
        squarify(children, [], width())



def squarify(remaining, current, x, y, dx, dy):
    head = remaining[0]
    tail = remaining[1:]
    if len(current) == 0 or worst(current, dy) >= worst([head] + current, dy):
        remaining2 = children[1:]
        if len(remaining2) == 0:
            layoutrow([c] + row)
        else:
            squarify(remaining2, [c] + row, w)
    else:
        layoutrow(current)
        squarify(remaining, [], )    
    

app = Bottle()

@route('/')
def index():
    pass

@route('/tree/<ftp_url>/<path:path>')
def tree(ftp_url, path):
    pass

run(app)