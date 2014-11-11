__author__ = 'HUNGPHONGPC'


def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)
    app.appstats_CALC_RPC_COSTS = True
    return app