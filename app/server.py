
import time
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import users

from src import config, store, model, sane, charting

class Handler(webapp.RequestHandler):
    def show(self, output):
        self.response.out.write(output)

    def render(self, template, **kw):
        from src import templating
        self.show(templating.render(template, **kw))

    def handle_exception(self, e, debug_mode):
        if isinstance(e, store.NotFoundError):
            logging.debug("NotFound: %s", e)
            self.error(404)
            self.render('404.html', title='404: Not found')
            return
        webapp.RequestHandler.handle_exception(self, e, debug_mode)


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
    def post(self):
        name = sane.valid_name(self.request.get('name'))
        user = users.get_current_user()
        logging.info('User %s is adding server: %s', user.email(), name)
        server = store.add_server(user.user_id(), name)
        self.redirect('/my/servers/agent/%s?added=1' % server.id())

class ServerAgent(Handler):
    def get(self, server_id):
        server = sane.valid_entity(model.Server, server_id)
        added = self.request.get('added') == '1'
        self.render('agent.html',
                title='Run agent on %s' % server.name,
                server=server, added=added)

class ServerView(Handler):
    def get(self, server_id):
        server = sane.valid_entity(model.Server, server_id)
        last_data_at = store.get_last_data_at(server_id)
        if last_data_at is not None:
            seconds_ago =int(time.time()) - last_data_at
        else:
            seconds_ago = None

        charts = charting.CHARTS
        time_from, time_to = charting.get_from_to_times()
        self.render('view.html', title=server.name, server=server,
                last_data_at=last_data_at, seconds_ago=seconds_ago,
                charts=charts,
                time_from=time_from, time_to=time_to)

class ServerChartdata(Handler):
    def get(self, server_id):
        server = sane.valid_entity(model.Server, server_id)
        time_from = sane.valid_int(self.request.get('time_from'))
        time_to = sane.valid_int(self.request.get('time_to'))
        chart = sane.valid_chart(self.request.get('chart'))

        timestamps = charting.generate_timestamps(time_from, time_to)
        graphs = charting.get_chart_graphs(server.id(), chart, timestamps)
        self.render('chartdata.xml', timestamps=timestamps,
                graphs=graphs, options=chart.options)

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
        self.show('OK')

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
            ('/postback/', Postback),
            ('/.*', CatchAll),
        ],
        debug=config.DEBUG)

def main():
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    from pylib import autoretry
    autoretry.autoretry_datastore_timeouts()
    main()

