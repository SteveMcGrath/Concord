from app import app

def app_factory(global_config, **local_config):
    return app.wsgi_app