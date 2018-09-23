from celery_pantry.custom_handler import CustomPantryHandler


class WorkerMonitor(CustomPantryHandler):

    def process_event(self, event, task):
        if event['type'].startswith('worker-'):
            print('State of workers:')
            for key, worker in self.state.workers.items():
                print('  -', key, worker.status_string)
