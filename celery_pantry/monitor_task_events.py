"""Monitor task updates and save them to a database using Django's ORM"""

import os
import logging
import threading
from queue import Queue, Empty
from signal import signal, SIGTERM

from celery import Celery

logger = logging.getLogger('monitor_task_events')


class TaskEventMonitor:

    def __init__(self, app: Celery):
        self.app = app
        self.state = app.events.State()
        self.receiver = None
        self.task_updates = Queue()
        self.save_tasks = True
        self.worker_thread = threading.Thread(
            target=self.save_task_updates,
            name='TaskEventMonitor worker'
        )

        signal(SIGTERM, self.stop)

    def capture(self):
        logger.info('Capturing task updates')
        self.worker_thread.start()

        try:
            with self.app.connection() as connection:
                self.receiver = self.app.events.Receiver(connection, handlers={
                    '*': self.process_event,
                })
                self.receiver.capture()
        except KeyboardInterrupt:
            self.stop()

    def stop(self, *args):
        logger.info('Stopping worker...')
        self.receiver.should_stop = True
        self.save_tasks = False
        self.worker_thread.join()
        logger.info('Worker stopped')

    def process_event(self, event):
        self.state.event(event)
        if event['type'].startswith('task-'):
            task = self.state.tasks.get(event['uuid'])
            self.task_updates.put(task.as_dict())

    def save_task_updates(self):
        while self.save_tasks:
            try:
                task = self.task_updates.get(timeout=2)
                logger.info('task: %s', task)
                # TODO: actually save the task info
            except Empty:
                continue


def monitor(app):
    TaskEventMonitor(app).capture()


if __name__ == '__main__':
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOGGING_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    monitor(Celery(
        os.getenv('CELERY_APP_NAME', 'example_tasks'),
        broker='amqp://{}:{}@{}//'.format(
            os.getenv('MQ_USER', 'example'),
            os.getenv('MQ_PASS', 'publicsecret'),
            os.getenv('MQ_HOST', 'localhost'),
        )
    ))
