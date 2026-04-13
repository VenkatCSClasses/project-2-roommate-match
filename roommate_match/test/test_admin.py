import unittest
from roommate_match.src.system import RoommateSystem
from roommate_match.src.admin import Admin

class TestAdmin(unittest.TestCase):
    
    def setUp(self):
        self.system = RoommateSystem()
        self.admin = Admin(1,"Admin1", "Admin1@gmail.com", "123")
        
    def test_add_student(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)

    def test_remove_student(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)
        student1 = self.admin.getStudentsByName("Julia")
        student1Id = self.admin.getStudentById(student1.id)
        self.admin.removeStudent(student1Id)
        self.assertEqual(len(self.system.students), 0)

    def test_view_all_students(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.admin.addStudent("Julia", "ju@gmail.com", "123", "Ithaca")
        self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")

        students = self.admin.viewAllStudents()
        self.assertEqual(len(students), 3)

    def test_get_student_by_name(self):
        student1 = self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        student2 = self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.assertEqual(self.admin.getStudentByName("Julia"), student1)
        self.assertEqual(self.admin.getStudentByName("Julia"), student2)


    def test_get_student_by_id(self):
        student1 = self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        student2 = self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.assertEqual(self.admin.getStudentById(student1.id), student1)
        self.assertEqual(self.admin.getStudentById(student2.id), student2)

    def test_finalize_pairing(self):
        student1 = self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        student2 = self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        result = self.admin.finalizePairing(student1.id, student2.id)
        self.assertEqual(result, "Pairing successful")
        self.assertEqual(student1.group_id, student2.group_id)
        self.assertEqual(len(self.system.matches), 1)

    def test_add_preference_option(self):
        self.admin.addPreferenceOption("Clean")
        self.assertIn("Clean", self.admin.preference_options)

    def test_interest_options(self):
        self.admin.addInterestOption("Sports")
        self.assertIn("Sports", self.system.interest_options)
        

if __name__ == "__main__":
    unittest.main()
