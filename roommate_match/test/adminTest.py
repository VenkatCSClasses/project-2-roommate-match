import unittest
from roommate_match.src.admin import Admin

class TestAdmin(unittest.TestCase):
    
    def test_Admin(self):
        admin = Admin()
        self.assertEqual(admin.students, [])
        self.assertEqual(admin.matches, [])

    def test_add_student(self):
        admin = Admin()
        admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")

        self.assertEqual(len(admin.students), 1)

    def test_remove_student(self):
        admin = Admin()
        admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(admin.students), 1)
        student1 = admin.getStudentsByName("Julia")
        student1Id = admin.getStudentById(student1.id)
        admin.removeStudent(student1Id)
        self.assertEqual(len(admin.students), 0)

    def test_view_all_students(self):
        admin = Admin()
        admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        admin.addStudent("Julia", "ju@gmail.com", "123", "Ithaca")
        admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")

        students = admin.viewAllStudents()
        self.assertEqual(len(students), 3)

    def test_get_student_by_name(self):
        admin = Admin()
        student1 = admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        student2 = admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.assertEqual(self.getStudentByName("Julia"), student1)
        self.assertEqual(self.getStudentByName("Julia"), student2)
        
        
    

if __name__ == "__main__":
    unittest.main()
