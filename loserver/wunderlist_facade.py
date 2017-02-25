#!/usr/bin/env python2

from properties import tokens
import datetime
import wunderpy2


def task_due_date(task):
    if 'due_date' in task:
        return datetime.datetime.strptime(task['due_date'], "%Y-%m-%d")
    return None


class WunderFacade(object):
    def __init__(self):
        api = wunderpy2.WunderApi()
        self.client = api.get_client(
            tokens['wunderlist_token'], tokens['wunderlist_client_id'])

    def get_list_id_by_title(self, title):
        found = [x for x in self.client.get_lists() if x['title'] == title]
        return found[0][wunderpy2.List.ID] if len(found) > 0 else None

    def get_tasks_on_list_by_title(self, title):
        lid = self.get_list_id_by_title(title)
        if lid is None:
            return []
        tasks = self.client.get_tasks(lid)
        tasks_with_ids = dict(
            [(tsk['id'], tsk['title']) for tsk in tasks])
        task_positions_obj = self.client.get_task_positions_obj(
            lid)['values']
        return [tasks_with_ids[x]
                for x in task_positions_obj if x in tasks_with_ids]

    def get_tasks_for_today(self):
        all_todo_tasks = [
            _task for _list in self.client.get_lists()
            for _task in self.client.get_tasks(_list['id'])]

        return [
            _task['title'] for _task in all_todo_tasks
            if 'due_date' in _task
            and task_due_date(_task) <= datetime.datetime.now()
        ]
