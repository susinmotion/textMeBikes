import unittest
import textMeBikes

class testFindNearStations(unittest.TestCase):
    def setUp(self):
        self.station_dict = textMeBikes.get_all_docks()

    def test_find_near_stations_returns_right_stations(self):
        near_stations = textMeBikes.find_near_stations(40.742, -74.000, self.station_dict)
        expected_stations = set([482, 453, 334, 434, 116, 470, 284])
        self.assertEqual(expected_stations, set(near_stations.keys()))
        # this test will fail if any of these stations ever go out of service =(

    def test_find_near_stations_error_if_too_far(self):
        with self.assertRaises(textMeBikes.NoStationsError) as e:
            textMeBikes.find_near_stations(35.682970, 139.805871, self.station_dict)
            textMeBikes.find_near_stations(40.831620, -73.943110, self.station_dict)

    def test_clean_stations_removes_out_of_service_stations(self):
        self.station_dict[389]["statusValue"] = "Not In Service"
        near_stations = textMeBikes.find_near_stations(40.7308224, -73.9789927, self.station_dict)
        self.assertNotIn(389, near_stations)

if __name__ == '__main__':
    unittest.main()

"""
class testAThing(unittest.TestCase):
    def setUp(self):
        pass

    def runTest(self):
        pass
"""