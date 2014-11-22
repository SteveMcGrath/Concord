#!/usr/bin/env python
from app import app

def app_factory(global_config, **local_config):
    return app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)