from random import randint
from .Student import Student
from .roommateRequest import roommateRequest
from .pairing import pairing

class RoommateSystem:
    def __init__(self):
        self.students = []
        self.admins = []
        self.preference_options = []
        self.interest_options = []
        self.pairings = []
        self.requests = []
        self.next_group_id = 1

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
        return student

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
    
    def viewStudents(self):
        return self.students
    
    def generateGroupId(self):
        newGroupId = randint(1,50)
        existing_ids = [s.groupID for s in self.students]
        while newGroupId in existing_ids:
            newGroupId = randint(1,50)
        
        return newGroupId


    def updateRequestList(self):
        for request in self.requests:
            if request.isAccepted() == True:
                senderID = request.getSenderId()
                group = []
                group.append(senderID)
                group.extend(request.getReceiverIds())     
                
                new_pairing = pairing(self.generateGroupId(), group)
                self.pairings.append(new_pairing)
                self.requests.remove(request)

            if request.isAccepted() == False:
                    self.requests.remove(request)

    def finalize_pairing(self):
        for student in self.students:
            for pairing in self.pairings:
                if student.id in pairing.students:
                    student.groupID = pairing.group_id
                self.pairings.remove(pairing)

    def removeAllPairings(self):
        self.pairings = []