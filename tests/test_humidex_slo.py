import unittest
from hamcrest import *
from mockito import *
from loserver import humidex_slo


class TestHumidexSLO_shallow_cache(unittest.TestCase):
    def test_should_load_first_data_on_init_to_shallow_cache(self):
        # given
        humidexDevicesFacade = mock()
        when(humidexDevicesFacade).get_humidex_indoor().thenReturn(
            (25.0, 20.0))
        when(humidexDevicesFacade).get_humidex_outdoor().thenReturn(
            (2.0, 80.0))

        # when
        humidex = humidex_slo.HumidexSLO(humidexDevicesFacade)

        # then
        assert_that(len(humidex.shallow_cache), equal_to(1))
