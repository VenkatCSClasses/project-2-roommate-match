import unittest
from roommate_match.src.system import RoommateSystem

class TestRoommateSystem(unittest.TestCase):

    def setUp(self):
        self.system = RoommateSystem()

    def test_add_student(self):
        self.system.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)

    def test_remove_student(self):
        student1 = self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.removeStudent(student1.id)
        self.assertEqual(len(self.system.students), 0)

    def test_get_student_by_name(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("Julia", "j2@test.com", "123", "CA")

        result = self.system.getStudentByName("Julia")
        self.assertEqual(len(result), 2)

    def test_get_student_by_id(self):
        student1 = self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student2 = self.system.addStudent("Julia", "j2@test.com", "123", "CA")
        result1 = self.system.getStudentById(student1)
        self.assertEqual(len(result1), 1)
        result2 = self.system.getStudentById(student2)
        self.assertEqual(len(result2), 1)

    def test_finalize_pairing(self):
        s1 = self.system.addStudent("April", "a@test.com", "123", "NY")
        s2 = self.system.addStudent("Bodb", "b@test.com", "123", "CA")

        result = self.system.finalizePairing(s1.id, s2.id)

        self.assertEqual(result, "Pairing successful")
        self.assertEqual(s1.groupID, s2.groupID)
        self.assertEqual(len(self.system.matches), 1)

if __name__ == "__main__":
    unittest.main()


    