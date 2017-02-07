import unittest
from hamcrest import assert_that, equal_to, is_
from mockito import when, mock
from loserver import humidex_slo
from matchers import is_sorted_by_timestamp


class TestHumidexSLO(unittest.TestCase):
    """
        Mocked humidex sensor will return
        in:  (15.0, 65.0), (16.0, 66.0), (17.0, 67.0) .... (35.0, 85.0)
        out: (-10.0, 50.0), (-9.0, 51,0),.. (0.0, 60.0) ...(10.0, 70.0)
    """

    def test_should_load_first_data_on_init_to_shallow_cache(self):
        # when
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)

        # then
        assert_that(len(humidex.shallow_cache), equal_to(1))
        assert_that(humidex.shallow_cache, is_(is_sorted_by_timestamp()))

    def test_should_put_data_sorted_to_shallow_cache(self):
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)

        # when
        for _ in range(10):
            humidex.fetch_current_humidex_from_sensors()

        # then
        assert_that(len(humidex.shallow_cache), equal_to(11))
        assert_that(humidex.shallow_cache, is_(is_sorted_by_timestamp()))

    def test_squeeze_should_compress_all_data_to_one_entry(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        for _ in range(9):
            humidex.fetch_current_humidex_from_sensors()
        assert_that(len(humidex.shallow_cache), equal_to(10))
        last_timestamp = humidex.shallow_cache[9].timestamp

        # when
        humidex.squeeze_shallow_cache_to_avg()

        # then
        assert_that(len(humidex.shallow_cache), equal_to(0))
        assert_that(len(humidex.avg_cache), equal_to(1))
        assert_that(humidex.avg_cache[0].indoor_data[0], equal_to(19.5))  # avg
        assert_that(humidex.avg_cache[0].indoor_data[1], equal_to(69.5))  # avg
        assert_that(humidex.avg_cache[0].outdoor_data[0], equal_to(-5.5))
        assert_that(humidex.avg_cache[0].outdoor_data[1], equal_to(54.5))
        assert_that(humidex.avg_cache[0].timestamp, equal_to(last_timestamp))

    def test_should_squeeze_two_times(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        for _ in range(9):
            humidex.fetch_current_humidex_from_sensors()
        assert_that(len(humidex.shallow_cache), equal_to(10))
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(9):
            humidex.fetch_current_humidex_from_sensors()
        assert_that(len(humidex.shallow_cache), equal_to(9))

        # when
        humidex.squeeze_shallow_cache_to_avg()

        # then
        assert_that(len(humidex.shallow_cache), equal_to(0))
        assert_that(len(humidex.avg_cache), equal_to(2))

    def test_should_flush_all_sqeezed_leave_last_one_when_first_invoke(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        for _ in range(4):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(4):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(4):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(4):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        assert_that(humidex.avg_cache, is_(is_sorted_by_timestamp()))
        assert_that(len(humidex.avg_cache), equal_to(4))
        assert_that(humidex.avg_cache[3].indoor_data[0], equal_to(29.5))

        # when
        humidex.flush_cache_to_db()

        # then
        given_to_write = self.humidex_db.to_write
        assert_that(len(given_to_write), equal_to(4))
        assert_that(given_to_write, is_(is_sorted_by_timestamp()))
        assert_that(len(humidex.avg_cache), equal_to(1))
        assert_that(humidex.avg_cache[0].indoor_data[0], equal_to(29.5))

    def test_should_flush_all_without_previously_left_when_two_times_fl(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()

        humidex.flush_cache_to_db()

        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        for _ in range(3):
            humidex.fetch_current_humidex_from_sensors()
        humidex.squeeze_shallow_cache_to_avg()
        assert_that(humidex.avg_cache[3].indoor_data[0], equal_to(32.0))

        # when
        humidex.flush_cache_to_db()

        # then
        given_to_write = self.humidex_db.to_write
        assert_that(len(given_to_write), equal_to(6))
        assert_that(given_to_write, is_(is_sorted_by_timestamp()))
        assert_that(len(humidex.avg_cache), equal_to(1))
        assert_that(humidex.avg_cache[0].indoor_data[0], equal_to(32.0))
        assert_that(given_to_write[5].indoor_data[0], equal_to(32.0))

    def test_squeeze_works_with_one_value_in_shallow(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        humidex.fetch_current_humidex_from_sensors()
        # when
        humidex.squeeze_shallow_cache_to_avg()
        # then
        assert_that(len(humidex.avg_cache), equal_to(1))

    def test_multiple_flushes(self):
        # given
        humidex = humidex_slo.HumidexSLO(
            self.humidexDevicesFacade, self.humidex_db)
        for _ in range(6):
            for _ in range(3):
                humidex.fetch_current_humidex_from_sensors()
                humidex.print_shallow()
                humidex.print_avg_cache()
                humidex.squeeze_shallow_cache_to_avg()
            humidex.flush_cache_to_db()
        humidex.flush_cache_to_db()

        # then
        given_to_write = self.humidex_db.to_write
        assert_that(len(given_to_write), equal_to(18))
        assert_that(given_to_write, is_(is_sorted_by_timestamp()))

    #
    #
    # ============= INITIALIZATION ===============
    def setUp(self):
        self.in_data_counter = 0
        self.out_data_counter = 0
        self.humidexDevicesFacade = mock()
        when(self.humidexDevicesFacade).get_humidex_indoor().thenAnswer(
            self.in_data_supplier)
        when(self.humidexDevicesFacade).get_humidex_outdoor().thenAnswer(
            self.out_data_supplier)
        self.humidex_db = FakeDB()

    def in_data_supplier(self):
        i = self.in_data_counter
        self.in_data_counter += 1
        return [(float(x), x + 50.) for x in range(15, 35)][i]

    def out_data_supplier(self):
        i = self.out_data_counter
        self.out_data_counter += 1
        return [(float(x), x + 60.) for x in range(-10, 10)][i]


class FakeDB(object):
    def __init__(self):
        self.to_write = []

    def append_entries(self, to_write):
        self.to_write += to_write
