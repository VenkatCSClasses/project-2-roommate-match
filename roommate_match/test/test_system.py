import unittest
from src.system import RoommateSystem
from src.roommateRequest import roommateRequest
from src.pairing import pairing

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

    def test_update_request_list_accepted(self):
        request = roommateRequest(1, 2, 3)
        request.accept_request(2) #all receivers accept
        request.accept_request(3)
        request.updateStatus()  #sets accepted = True
        
        initial_len = len(self.system.pairings)
        self.system.updateRequestList(request)
        self.assertEqual(len(self.system.pairings), initial_len + 1)

        new_pairing = self.system.pairings[-1]
        self.assertIn(1, new_pairing.group)
        self.assertIn(2, new_pairing.group)
        self.assertIn(3, new_pairing.group)

    def test_update_request_list_rejected(self):
        request = roommateRequest(1, 2, 3)
        request.reject_request(2) #reject
        request.updateStatus()  #sets accepted = True
        self.system.requests.append(request)
        initial_len = len(self.system.requests)
        self.system.updateRequestList(request)

        self.assertEqual(len(self.system.requests), initial_len - 1)
        

if __name__ == "__main__":
    unittest.main()


    