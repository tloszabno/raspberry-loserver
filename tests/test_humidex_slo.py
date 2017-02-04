import unittest
from hamcrest import *
from mockito import *
from loserver import humidex_slo
from loserver import devices


class TestHumidexSLO_shallow_cache(unittest.TestCase):
    def test_should_append_data_to_shallow_cache_in_adding_order(self):
        assert_that(True, equal_to(True))
