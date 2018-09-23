"""Monitor task updates and save them to a database using Django's ORM"""

import os
import logging
import threading
import traceback
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

        from celery_pantry.settings import pantry_settings

        handler_class = pantry_settings.CUSTOM_HANDLER
        if handler_class:
            from celery_pantry.custom_handler import CustomPantryHandler
            assert issubclass(handler_class, CustomPantryHandler)
            self._custom_handler = handler_class(self.state)
        else:
            self._custom_handler = None

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
            pass
        finally:
            self.stop()

    def stop(self, *args):
        logger.info('Stopping worker...')
        if self.receiver:
            self.receiver.should_stop = True
        self.save_tasks = False
        self.worker_thread.join()
        logger.info('Worker stopped')

    def process_event(self, event):
        self.state.event(event)

        if event['type'].startswith('task-'):
            task = self.state.tasks.get(event['uuid'])
            self.task_updates.put(task.as_dict())
        else:
            task = None

        if self._custom_handler:
            # noinspection PyBroadException
            try:
                self._custom_handler.process_event(event, task)
            except Exception:  # noqa
                logger.warning('Exception in custom handler: %s',
                               traceback.format_exc())

    def save_task_updates(self):
        from celery_pantry.models import Task

        while self.save_tasks:
            # noinspection PyBroadException
            try:
                task = self.task_updates.get(timeout=2)
                logger.debug('task: %s', task)
                task_id = task.pop('uuid')
                task['worker'] = task['worker'].hostname

                try:
                    obj = Task.objects.get(id=task_id)
                    obj.data = task
                    obj.save()
                except Task.DoesNotExist:
                    Task.objects.create(id=task_id, data=task)

            except Empty:
                continue

            except Exception:  # noqa
                logger.warning('Exception in task update thread: %s',
                               traceback.format_exc())


def monitor(app):
    TaskEventMonitor(app).capture()


if __name__ == '__main__':
    import django

    django.setup()
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOGGING_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    monitor(Celery(
        os.getenv('CELERY_APP_NAME', 'example_tasks'),
        broker='amqp://{}:{}@{}//'.format(
            os.getenv('MQ_USER', 'example'),
            os.getenv('MQ_PASS', 'publicsecret'),
            os.getenv('MQ_HOST', 'mq'),
        )
    ))
