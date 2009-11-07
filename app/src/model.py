
import time
import pickle
from google.appengine.ext import db

class Server(db.Model):
    user_id = db.StringProperty(required=True)
    name = db.StringProperty()
    secret = db.StringProperty(required=True)

    def id(self):
        return self.key().id()

    def get_secret_key(self):
        return '%s_%s' % (self.id(), self.secret)

    @classmethod
    def split_secret_key(cls, secret_key):
        """Splits the secret_key into server_id and secret.
        """
        server_id, secret = secret_key.split('_', 1)
        return int(server_id), secret


class Stage(db.Model):
    """A staging area.
    It is connected to a server by its key_name.
    The key_name has format: SERVERID_DURATION
    """
    end = db.IntegerProperty(required=True)
    sums = db.BlobProperty()
    counts = db.BlobProperty()
    last_data_at = db.IntegerProperty()

    @classmethod
    def prepare(cls, server_id, duration):
        key_name = cls.build_key_name(server_id, duration)
        # The stage ends at duration//2.
        # The point for it will be at 0.
        stage = Stage(key_name=key_name, end=duration//2)
        stage.update_samples({}, {})
        stage.last_data_at = None
        return stage

    @classmethod
    def build_key_name(cls, server_id, duration):
        return '%s_%s' % (server_id, duration)

    def update_samples(self, sums, counts):
        self.sums = pickle.dumps(sums, 2)
        self.counts = pickle.dumps(counts, 2)
        self.last_data_at = int(time.time())

    def get_sums(self):
        """Returns a dict with source:value items.
        """
        return pickle.loads(self.sums)
    def get_counts(self):
        """Returns a dict with source:count items.
        """
        return pickle.loads(self.counts)

    def get_avg_values(self):
        sums = self.get_sums()
        counts = self.get_counts()
        avg_values = {}
        for key, sum_value in sums.iteritems():
            avg_values[key] = sum_value / counts[key]

        return avg_values

    def get_server_id(self):
        return int(_split_key_name(self)[0])

    def get_duration(self):
        return int(_split_key_name(self)[1])


class Point(db.Model):
    """A data point.
    Its key_name has format: SERVERID_DURATION_ZEROPADDEDTIMESTAMP
    """
    values = db.BlobProperty()

    @classmethod
    def build_key_name(cls, server_id, duration, timestamp):
        return '%s_%s_%011d' % (server_id, duration, timestamp)

    @classmethod
    def prepare(cls, server_id, duration, timestamp, values):
        key_name = cls.build_key_name(server_id, duration, timestamp)
        point = Point(key_name=key_name)
        point.set_values(values)
        return point

    def get_values(self):
        """Returns a dict with source:value items.
        """
        return pickle.loads(self.values)
    def set_values(self, values):
        self.values = pickle.dumps(values)

    def get_timestamp(self):
        return int(_split_key_name(self)[2])


def _split_key_name(entity):
    key_name = entity.key().name()
    return key_name.split('_')
