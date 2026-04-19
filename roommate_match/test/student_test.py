import unittest
from unittest.mock import patch, MagicMock
from src.Student import Student
from src.system import RoommateSystem

class StudentTest(unittest.TestCase):
    student1 = Student(123, "John Doe", "john.doe@example.com", "password123", "New York")
    student2 = Student(234, "Jane Smith", "jane.smith@example.com", "password456", "Los Angeles")

    def test_sendRequest(self):
        system = RoommateSystem()
        sender = system.addStudent("Alice", "alice@test.com", "123", "NY")
        recipient = system.addStudent("Bob", "bob@test.com", "123", "CA")

        sender.sendRequest(recipient.id, system)

        # Ensures there is 1 request in the list
        self.assertEqual(len(recipient.requests), 1)

    def test_respondRequest(self):
        system = RoommateSystem()
        sender = system.addStudent("Alice", "alice@test.com", "123", "NY")
        recipient = system.addStudent("Bob", "bob@test.com", "123", "CA")

        sender.sendRequest(recipient.id, system)

        # Accepts request
        req_id = recipient.requests[0]["request_id"]
        recipient.respondRequest(req_id, system, accept=True)
        self.assertEqual(recipient.requests[0]["status"], "accepted")

        # Denies request
        sender.sendRequest(recipient.id, system)
        req_id2 = recipient.requests[1]["request_id"]
        recipient.respondRequest(req_id2, system, accept=False)
        self.assertEqual(recipient.requests[1]["status"], "denied")

        # Invalid request
        with self.assertRaises(ValueError):
            recipient.respondRequest(9999, system, accept=True)

    
    def test_updatePassword(self):
        self.student1.updatePassword("newpassword123")
        self.assertEqual(self.student1.password, "newpassword123")

        self.student2.updatePassword("newpassword456")
        self.assertEqual(self.student2.password, "newpassword456")

        with self.assertRaises(ValueError):
            self.student1.updatePassword("")

        with self.assertRaises(ValueError):
            self.student2.updatePassword("")

    def test_updateName(self):
        self.student1.updateName("John Doe")
        self.assertEqual(self.student1.name, "John Doe")

        self.student2.updateName("Juliet Smith")
        self.assertEqual(self.student2.name, "Juliet Smith")

        with self.assertRaises(ValueError):
            self.student1.updateName("")

        with self.assertRaises(ValueError):
            self.student2.updateName("")

    def test_updateHometown(self):
        self.student1.updateHometown("Chicago")
        self.assertEqual(self.student1.hometown, "Chicago")

        self.student2.updateHometown("Nashville")
        self.assertEqual(self.student2.hometown, "Nashville")


        self.student1.updateHometown("")
        self.assertEqual(self.student1.hometown, "")

        self.student2.updateHometown("")
        self.assertEqual(self.student2.hometown, "")
    

    @patch("sqlite3.connect")
    @patch("builtins.input")
    def test_updateInterests(self, mock_input, mock_connect):

        mock_input.side_effect = [
            "1", "add",       # add Music
            "1", "add",       # duplicate add
            "999",            # invalid ID
            "2", "remove",    # remove Sports
            "q"               # quit
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "Music"), (2, "Sports")]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        s = Student(1, "Alex", "a@b.com", "pw", "NY")
        s.interests = ["Sports"]

        s.updateInterests("fake.db")

        # Test music was added
        self.assertIn("Music", s.interests)

        # Test duplicate add did not create a second Music
        self.assertEqual(s.interests.count("Music"), 1)

        # Test invalid ID did not change interests
        self.assertIn("Sports", s.interests)

        # Test sports was removed once
        self.assertEqual(s.interests.count("Sports"), 1)

    @patch("sqlite3.connect")
    @patch("builtins.input")
    def test_updatePreferences(self, mock_input, mock_connect):

        mock_input.side_effect = [
            "1", "add",
            "1", "add",
            "999",
            "2", "remove",
            "q"
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "Cleanliness"), (2, "Quiet Hours")]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        s = Student(1, "Alex", "a@b.com", "pw", "NY")
        s.preferences = ["Quiet Hours"]

        s.updatePreferences("fake.db")

        # Test cleanliness was added
        self.assertIn("Cleanliness", s.preferences)

        # Test duplicate add did not create a second cleanliness
        self.assertEqual(s.preferences.count("Cleanliness"), 1)

        # Test invalid ID did not change preferences
        self.assertIn("Quiet Hours", s.preferences)

        # Test quiet hours was removed once
        self.assertEqual(s.preferences.count("Quiet Hours"), 1)


    def test_viewStudents(self):
        system = RoommateSystem()
        system.addStudent("Alice", "alice@test.com", "123", "NY")
        system.addStudent("Bob", "bob@test.com", "123", "CA")
        system.addStudent("Charlie", "charlie@test.com", "123", "TX")

        students = system.viewStudents()

        # Ensures all 3 students are in list
        self.assertEqual(len(students), 3)
        for s in students:
            self.assertIsInstance(s, Student)

        # Checks each student in list to ensure they are correct
        names = [s.name for s in students]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)

    def test_searchStudents(self):
        system = RoommateSystem()
        s1 = system.addStudent("Alice", "alice@test.com", "123", "NY")
        s2 = system.addStudent("Bob", "bob@test.com", "123", "CA")

        # Checks result is Bob
        result = self.student1.searchStudents(str(s2.id), system)
        self.assertEqual(result.name, "Bob")

        # If ID is out of bounds
        with self.assertRaises(ValueError):
            self.student1.searchStudents("999", system)

        # If search field is not student ID
        with self.assertRaises(ValueError):
            self.student1.searchStudents("Alice", system)



if __name__ == '__main__':
    unittest.main()