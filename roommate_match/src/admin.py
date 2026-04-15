from random import randint
from .Student import Student

class Admin:
    def __init__(self, id, name, email, password, system): 
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.system = system

    def addStudent(self, name, email, password, hometown):
        self.system.addStudent(name, email, password, hometown)

    def removeStudent(self, id):
        self.system.students.remove(self.system.getStudentById(id))

    def viewAllStudents(self):
        return self.system.students

    def getStudentByName(self, name):
        students = self.system.getStudentByName(name)
        if  len(students) == 0:
            print("Student " + name + " not found")
        return students

    def getStudentById(self, id):
        student = self.system.getStudentById(id)
        if  student == None:
            print("Student " + id + " not found")
        return student
            
    def finalizePairing(self, id1, id2):
        #puts both students in the same group and adds the group to the matches list
        self.system.finalizePairing(id1, id2)

    def addPreferenceOption(self, preference):
        self.system.preference_options.append(preference)
    
    def viewPreferenceOptions(self):
        return self.system.preference_options

    def addInterestOption(self, interest):
        self.system.interest_options.append(interest)
    
    def viewInterestOptions(self):
        return self.system.interest_options