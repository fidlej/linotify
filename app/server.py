
from waddon import config
config.DEBUG = True

import time
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

from waddon.handling import show, handle_errors
from waddon.nocsrf import prevent_csrf
from src import store, model, sane


class Handler(webapp.RequestHandler):
    show = show

    def render(self, template, **kw):
        from waddon import templating, nocsrf
        from src import formatting
        def ensure_csrf_token():
            return nocsrf.ensure_csrf_token(self)

        args = dict(
                req=sane.RequestContext(self.request),
                user=users.get_current_user(),
                formatting=formatting,
                ensure_csrf_token=ensure_csrf_token
                )
        args.update(kw)
        output = templating.render(template, **args)
        self.show(output)

    def handle_exception(self, e, debug_mode):
        if isinstance(e, store.NotFoundError):
            logging.debug('NotFound: %s', e)
            self.error(404)
            if self.request.method == 'GET':
                self.render('404.html', title='404: Not found')
            else:
                self.show(str(e))

            return

        handle_errors(self, e, debug_mode)

class Index(Handler):
    def get(self):
        self.render('index.html', title='Linotify')

class About(Handler):
    def get(self):
        self.render('about.html', title='About Linotify')

class Logout(Handler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

class Servers(Handler):
    def get(self):
        user = users.get_current_user()
        servers = store.find_servers(user.user_id())
        self.render('servers.html', title='Servers', servers=servers)

class ServerAdd(Handler):
    @prevent_csrf
    def post(self):
        name = sane.valid_name(self.request.get('name'))
        user = users.get_current_user()
        logging.info('User %s is adding server: %s', user.email(), name)
        server = store.add_server(user.user_id(), name)
        store.ensure_user_profile(user)
        self.redirect('/my/servers/agent/%s?added=1' % server.id())

class ServerAgent(Handler):
    def get(self, server_id):
        server = sane.valid_entity(model.Server, server_id)
        added = self.request.get('added') == '1'
        if added:
            title = u'Start sending the values'
        else:
            title = u'Server %s setup' % server.name

        self.render('agent.html',
                title=title,
                server=server, added=added)

class ServerView(Handler):
    def get(self, server_id):
        from src import charting, chartdef
        days = sane.valid_int(self.request.get('days'), min_value=1)
        server = sane.valid_entity(model.Server, server_id)
        last_data_at = store.get_last_data_at(server_id)
        if last_data_at is not None:
            seconds_ago =int(time.time()) - last_data_at
        else:
            seconds_ago = None

        charts = chartdef.CHARTS
        time_from, time_to = charting.get_time_range(days,
                sane.RequestContext(self.request))
        self.render('view.html', title=server.name, server=server,
                last_data_at=last_data_at, seconds_ago=seconds_ago,
                charts=charts, days=days,
                time_from=time_from, time_to=time_to)

class ServerChartdata(Handler):
    def get(self, server_id):
        from src import charting
        server = sane.valid_entity(model.Server, server_id)
        time_from = sane.valid_int(self.request.get('time_from'))
        time_to = sane.valid_int(self.request.get('time_to'))
        chart = sane.valid_chart(self.request.get('chart'))

        timestamps = charting.generate_timestamps(time_from, time_to)
        graphs = charting.get_chart_graphs(server.id(), chart, timestamps)
        self.render('chartdata.xml', timestamps=timestamps,
                chart=chart, graphs=graphs)
        self.response.headers.add_header('Content-Type',
                'text/xml; charset=utf-8')

class Notice(Handler):
    def get(self):
        #TODO: implement
        self.show('OK')

class Postback(Handler):
    def post(self):
        from src import posting
        payload = self.request.get('payload')
        data = posting.parse_payload(payload)
        posting.update_stats(data)
        self.show(posting.comment_agent_version(data))

class DbUpdate(Handler):
    def get(self):
        from src import cleaning
        info = cleaning.remove_old_points()
        self.show(info)

class CatchAll(Handler):
    def get(self):
        logging.info('Wrong path: %s', self.request.path)
        raise store.NotFoundError

    def post(self):
        self.get()

app = webapp.WSGIApplication(
        [
            ('/', Index),
            ('/about', About),
            ('/logout', Logout),
            ('/my/servers', Servers),
            ('/my/servers/add', ServerAdd),
            ('/my/servers/agent/(.*)', ServerAgent),
            ('/my/servers/view/(.*)', ServerView),
            ('/my/servers/chartdata/(.*)', ServerChartdata),
            ('/cron/notice', Notice),
            ('/postback', Postback),
            ('/db_update', DbUpdate),
            ('/.*', CatchAll),
        ],
        debug=config.DEBUG)

#from src.profiling import profiled
#@profiled
def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    from pylib import autoretry
    autoretry.autoretry_datastore_timeouts()
    main()

