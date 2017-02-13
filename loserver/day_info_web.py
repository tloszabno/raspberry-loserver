import datetime
import locale


class DayInfoWeb(object):
    def __init__(self):
        locale.setlocale(locale.LC_TIME, "pl_PL.utf8")

    def get_day_info(self):
        now = datetime.datetime.now()
        date = now.strftime('%d %b %Y')
        time = now.strftime('%H:%M')
        return {
            'date': date,
            'time': time,
            'messages': []
        }
