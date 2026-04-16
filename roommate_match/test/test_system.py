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
        studentID = student[0].id
        self.system.removeStudent(student[0].id)
        self.assertEqual(len(self.system.students), 0)
        self.assertEqual(self.system.removeStudent(705000000), "There is no student with id: 705000000")
        self.assertEqual(self.system.removeStudent(studentID), "There is no student with id: " + str(studentID))
        

    def test_get_student_by_name(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("Julia", "julia@test.com", "123", "CA")
        self.system.addStudent("Bob", "Bob@test.com", "123", "CA")
        student = self.system.getStudentByName("Julia")
        student = self.system.getStudentByName("Bob")
        self.assertEqual(len(student), 1)
        student = self.system.getStudentByName("Julia D")
        self.assertEqual(len(student), 0)

    def test_get_student_by_id(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student1 = self.system.students[0]
        foundById1 = self.system.getStudentById(student1.id)
        self.assertEqual(foundById1, student1)
        self.assertEqual(self.system.getStudentById(705000000), None)

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


    