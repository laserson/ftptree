from bottle import Bottle, route, run


app = Bottle()

@route('/')
def index():
    pass

@route('/tree/<ftp_url>/<path:path>')
def tree(ftp_url, path):
    pass

run(app)