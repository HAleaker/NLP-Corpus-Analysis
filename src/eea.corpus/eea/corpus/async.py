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


def redis_conn