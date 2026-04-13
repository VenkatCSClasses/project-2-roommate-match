from random import randint
"from roommate_match.src.student import Student"

class Admin:
    def __init__(self, id, name, email, password, system): 
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.system = system

    def addStudent(self, name, email, password, hometown):
        pass

    def removeStudent(self, id):
        pass

    def viewAllStudents(self):
        return self.system.students

    def getStudentByName(self, name):
        pass

    def getStudentById(self, id):
        pass
            
    def finalizePairing(self, student1_id, student2_id):
        #puts both students in the same group and adds the group to the matches list
        pass

    def addPreferenceOption(self, preference):
        pass
    
    def viewPreferenceOptions(self):
        pass

    def addInterestOption(self, preference):
        pass
    
    def viewInterestOptions(self):
        pass