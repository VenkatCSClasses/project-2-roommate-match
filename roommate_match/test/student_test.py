import unittest
from roommate_match.src.Student import Student

class StudentTest(unittest.TestCase):
    student1 = Student(123, "John Doe", "john.doe@example.com", "password123", "New York")
    student2 = Student(234, "Jane Smith", "jane.smith@example.com", "password456", "Los Angeles")

    def test_updatePassword(self):
        self.student1.updatePassword("newpassword123")
        self.assertEqual(self.student1.password, "newpassword123")

        with self.assertRaises(ValueError):
            self.student1.updatePassword("")

    def test_updateName(self):
        self.student1.updateName("Johnathan Doe")
        self.assertEqual(self.student1.name, "Johnathan Doe")

        with self.assertRaises(ValueError):
            self.student1.updateName("")

    def test_updateHometown(self):
        self.student1.updateHometown("Chicago")
        self.assertEqual(self.student1.hometown, "Chicago")

        self.student1.updateHometown("")
        self.assertEqual(self.student1.hometown, "")


if __name__ == '__main__':
    unittest.main()