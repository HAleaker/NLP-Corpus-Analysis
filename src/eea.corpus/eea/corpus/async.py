from flask import Flask
from pkg_resources import resource_filename
from pyramid.paster import bootstrap
from redis import Redis
from redis.exceptions import ConnectionError
from rq import Queue, Worker, Connection
from rq.registry import StartedJobRegistry
from urllib import parse
import click
import logging
import os
import rq_dashboard


logger = logging.getLogger('eea.corpus')


def redis_connection():
    redis_uri = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    p = parse.urlparse(redis_uri)
    host, port = p.netloc.split(':')
    db = len(p.path) > 1 and p.path[1:] or '0'
    conn = Redis(host=host, port=port, db=db)
    return conn


def make_queue(name='default'):
    queue = Queue(connection=redis_connection())
    return queue


queue = make_queue()


@click.command()
@click.argument('config_uri')
def worker(config_uri):
    """ Console entry script that starts a worker process
    """
    # TODO: import spacy's model to share it between workers

    pyramid_env = bootstrap(config_uri)

    # this conflicts with normal worker output
    # TODO: solve logging for the console
    # Setu