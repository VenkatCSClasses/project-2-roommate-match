from random import randint
from .Student import Student

class RoommateSystem:
    def __init__(self):
        self.students = []
        #self.matches = []
        self.preference_options = []
        self.interest_options = []

    def generateId(self):
        newId = int("705" + str(randint(100000, 999999)))
        existing_ids = [s.id for s in self.students]

        while newId in existing_ids:
            newId = int("705" + str(randint(100000, 999999)))

        return newId

    def addStudent(self, name, email, password, hometown):
        student_id = self.generateId()
        student = Student(student_id, name, email, password, hometown)
        self.students.append(student)

    def removeStudent(self, id):
        for student in self.students:
            if student.id == id:
                self.students.remove(student)
                return f"Student: {student} was successfully removed"
        return f"There is no student with id: {id}"

    def getStudentByName(self, name):
        studentList = []
        for student in self.students:
            if student.name == name:
                studentList.append(student)
        return studentList

    def getStudentById(self, id):
        for student in self.students:
            if student.id == id:
                return student
        return None
    
    def gerenateGroupId(self):
        newGroupId = randint(1,10)
        existing_ids = [s.groupID for s in self.students]
        while newGroupId in existing_ids:
            newGroupId = randint(1,10)
        
        return newGroupId

    def finalizePairing(self, id1, id2):
        student1 = self.getStudentById(id1)
        student2 = self.getStudentById(id2)

        groupId = self.gerenateGroupId()
        student1.groupID = groupId
        student2.groupID = groupId  