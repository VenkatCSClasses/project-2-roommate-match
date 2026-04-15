import unittest
from src.roommateRequest import roommateRequest

class TestRoommateRequest(unittest.TestCase):

    def setUp(self):
        self.request1 = roommateRequest(1, 2)
        self.request2 = roommateRequest(3, 4, 5, 6)

    def test_initial_status(self):
        self.assertIsNone(self.request1.getStatus())
        self.assertIsNone(self.request2.getStatus())

    def test_accept_request(self):
        self.request1.accept_request()
        self.assertTrue(self.request1.getStatus())

    def test_reject_request(self):
        self.request2.reject_request()
        self.assertFalse(self.request2.getStatus())

    def test_get_sender_id(self):
        self.assertEqual(self.request1.getSenderId(), 1)
        self.assertFalse(self.request1.getSenderId() == 2)

    def test_get_receiver1_id(self):
        self.assertEqual(self.request1.getReceiver1Id(), 2)
        self.assertFalse(self.request1.getReceiver1Id() == 1)
        self.assertEqual(self.request2.getReceiver1Id(), 4)

    def test_get_receiver2_id(self):
        self.assertEqual(self.request2.getReceiver2Id(), 5)
        self.assertFalse(self.request2.getReceiver2Id() == 3)
        self.assertIsNone(self.request1.getReceiver2Id())

    def test_get_receiver3_id(self):
        self.assertEqual(self.request2.getReceiver3Id(), 6)
        self.assertFalse(self.request2.getReceiver3Id() == 4)
        self.assertIsNone(self.request1.getReceiver3Id())

if __name__ == '__main__':
    unittest.main()