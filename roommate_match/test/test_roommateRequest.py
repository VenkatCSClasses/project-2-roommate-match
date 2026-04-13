import unittest
from src.roommateRequest import roommateRequest

class TestRoommateRequest(unittest.TestCase):

    def setUp(self):
        self.request = roommateRequest(1, 2)

    def test_initial_status(self):
        self.assertIsNone(self.request.getStatus())

    def test_accept_request(self):
        self.request.accept_request()
        self.assertTrue(self.request.getStatus())

    def test_reject_request(self):
        self.request.reject_request()
        self.assertFalse(self.request.getStatus())

    def test_get_sender_id(self):
        self.assertEqual(self.request.getSenderId(), 1)
        self.assertFalse(self.request.getSenderId() == 2)

    def test_get_receiver_id(self):
        self.assertEqual(self.request.getReceiverId(), 2)
        self.assertFalse(self.request.getReceiverId() == 1)

if __name__ == '__main__':
    unittest.main()