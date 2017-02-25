class WunderListWeb(object):
    def __init__(self, wunder_list_slo):
        self.wunder_list_slo = wunder_list_slo

    def get_today_tasks(self):
        return self.format_tasks(self.wunder_list_slo.get_tasks_for_today())

    def get_todo_dom_tasks(self):
        return  self.format_tasks(self.wunder_list_slo.get_tasks_from_TODO_dom())

    def format_tasks(self, tasks):
        return {
            'list': tasks,
            'more': False
        }

