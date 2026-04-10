import unittest
from admin import Admin

class AdminTest(unittest.TestCase):
    
    def test_admin(self):
        admin = Admin()
        self.assertEqual(admin.students, [])
        self.assertEqual(admin.matches, [])

if __name__ == "__main__":
    unittest.main()
