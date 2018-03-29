
from gunicorn.app.base import BaseApplication
from scl_transport.api.api import create_app


class GunicornApp(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.iteritems()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.iteritems():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    app = create_app()
    host = "0.0.0.0"

    options = {
        'bind': '{host}:{port}'.format(host=host, port=5002),
    }
    GunicornApp(app, options).run()


if __name__ == '__main__':
    main()
