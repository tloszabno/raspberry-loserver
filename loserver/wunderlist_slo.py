import threading
import traceback


class WunderSLO(object):
    def __init__(self, wunder_facade):
        self.wunder_facade = wunder_facade
        self.today_tasks = []
        self.todo_dom_tasks = []
        self.lock = threading.RLock()
        self.update_cache()

    def get_tasks_for_today(self):
        return self.today_tasks[:]

    def get_tasks_from_TODO_dom(self):
        return self.todo_dom_tasks[:]

    def update_cache(self):
        with self.lock:
            try:
                self.today_tasks = self.wunder_facade.get_tasks_for_today()
                self.todo_dom_tasks = \
                    self.wunder_facade.get_tasks_on_list_by_title('TODO Dom')
            except Exception as e:
                traceback.print_stack()  # TODO: add some common logger
