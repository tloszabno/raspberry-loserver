class HumidexWeb(object):
    def __init__(self, humidex_slo):
        self.humidex_slo = humidex_slo

    def get_humidex_info(self):
        return self.humidex_slo.get_last()
