import unittest
from roommate_match.src.pairing import pairing

class TestPairing(unittest.TestCase):
    def setUp(self):
        self.pair = pairing(1, 2, 3)

    def test_get_user1_id(self):
        self.assertEqual(self.pair.get_user1_id(), 1)

    def test_get_user2_id(self):
        self.assertEqual(self.pair.get_user2_id(), 2)
    
    def test_get_user3_id(self):
        self.assertEqual(self.pair.get_user3_id(), 3)

    def test_get_user4_id(self):
        self.assertIsNone(self.pair.get_user4_id())