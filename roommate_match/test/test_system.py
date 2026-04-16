import unittest
from src.system import RoommateSystem

class TestRoommateSystem(unittest.TestCase):

    def setUp(self):
        self.system = RoommateSystem()

    def test_add_student(self):
        self.system.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)

    def test_remove_student(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student = self.system.getStudentByName("Julia")
        self.system.removeStudent(student[0].id)
        self.assertEqual(len(self.system.students), 0)

    def test_get_student_by_name(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student = self.system.getStudentByName("Julia")
        self.assertEqual(len(student), 1)

    def test_get_student_by_id(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student1 = self.system.students[0]
        foundById1 = self.system.getStudentById(student1.id)
        self.assertEqual(foundById1, student1)

    def test_finalize_pairing(self):
        self.system.addStudent("April", "a@test.com", "123", "NY")
        self.system.addStudent("Bob", "b@test.com", "123", "CA")
        
        aprilStudents = self.system.getStudentByName("April")
        s1 = aprilStudents[0]
        
        bobStudents = self.system.getStudentByName("Bob")
        s2 = bobStudents[0]
        
        self.system.finalizePairing(s1.id, s2.id)
        self.assertEqual(s1.groupID, s2.groupID)
        

if __name__ == "__main__":
    unittest.main()


    