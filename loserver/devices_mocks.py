class HumidexDevicesFacadeMock(object):
    def get_humidex_indoor(self):
        return (20.0, 70.0)

    def get_humidex_outdoor(self):
        return (0.0, 80.0)


class PMSensorDeviceFacadeMock(object):
    def update_reads(self):
        pass

    def get(self):
        return (1.0, 2.0), (3.0, 4.0)
