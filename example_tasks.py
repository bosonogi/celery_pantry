import os
import time
import random

from celery import Celery

queue = 'amqp://{}:{}@{}//'.format(
    os.getenv('MQ_USER', 'example'),
    os.getenv('MQ_PASS', 'publicsecret'),
    os.getenv('MQ_HOST', 'mq'),
)
results = 'db+postgresql://{}:{}@{}/{}'.format(
    os.getenv('PG_USER', 'example'),
    os.getenv('PG_PASS', 'publicsecret'),
    os.getenv('PG_HOST', 'db'),
    os.getenv('PG_DB', 'pantry'),
)

app = Celery('example_tasks', backend=results, broker=queue)
app.conf.result_expires = None
app.conf.worker_prefetch_multiplier = 1
app.conf.beat_schedule = {
    'add-every-5-seconds': {
        'task': 'example_tasks.add',
        'schedule': 5.0,
        'args': (2, 3)
    },
    'mul-every-4-seconds': {
        'task': 'example_tasks.mul',
        'schedule': 4.0,
        'args': (3, 4)
    },
}


@app.task
def add(a, b):
    print("Executing 'add' task")
    time.sleep(random.randint(1, 7))
    return a + b


@app.task
def mul(a, b):
    print("Executing 'mul' task")
    time.sleep(random.randint(1, 7))
    return a * b
