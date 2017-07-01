import datetime
import locale


class DayInfoWeb(object):
    def __init__(self, wunder_slo):
        locale.setlocale(locale.LC_TIME, "pl_PL.utf8")
        self.wunder_slo = wunder_slo

    def get_day_info(self):
        now = datetime.datetime.now()
        date = now.strftime('%d %b %Y')
        time = now.strftime('%H:%M')
        return {
            'date': date,
            'time': time,
            'messages': ["No messages", "Just smile ;)"]
        }
