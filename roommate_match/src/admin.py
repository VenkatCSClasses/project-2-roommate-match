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
        self.system.addStudent(name, email, password, hometown)

    def removeStudent(self, id):
        self.system.students.remove(self.system.getStudentById(id))

    def viewAllStudents(self):
        return self.system.students

    def getStudentByName(self, name):
        return self.system.getStudentByName(name)

    def getStudentById(self, id):
       return self.system.getStudentById(id)
            
    def finalizePairing(self, id1, id2):
        #puts both students in the same group and adds the group to the matches list
        return self.system.finalizePairing(id1, id2)

    def addPreferenceOption(self, preference):
        self.system.preference_options.append(preference)
    
    def viewPreferenceOptions(self):
        return self.system.preference_options

    def addInterestOption(self, interest):
        self.system.interest_options.append(interest)
    
    def viewInterestOptions(self):
        return self.system.interest_options