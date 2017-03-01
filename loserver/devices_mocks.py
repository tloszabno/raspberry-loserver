class HumidexDevicesFacadeMock(object):
    def get_humidex_indoor(self):
        return (20.0, 70.0)

    def get_humidex_outdoor(self):
        return (0.0, 80.0)
