class Student:
    def __init__(self, id: int, name: str, email: str, password: str, hometown: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.hometown = hometown
        self.interests = []
        self.preferences = []
        self.groupID = -1  # No group assigned

    #Get methods
    def getID(self):
        #Return the student's ID
        pass

    def getName(self):
        #Return the student's name
        pass

    def getEmail(self):
        #Return the student's email
        pass

    def getPassword(self):
        #Return the student's password
        pass

    def getHometown(self):
        #Return the student's hometown
        pass



    def sendRequest(self, other_student):
        #Send a roommate request to another student using their student ID only
        pass

    def respondRequest(self, other_student, response: str):
        #Respond to a roommate request from another student with "accept" or "reject"
        pass

    def updatePassword(self, new_password: str):
        #Update the student's password
        pass

    def updateName(self, new_name: str):
        #Update the student's name
        pass

    def updateHometown(self, new_hometown: str):
        #Update the student's hometown
        pass

    def updateInterests(self, new_interests: list):
        #Update the student's interests
        pass

    def updatePreferences(self, new_preferences: list):
        #Update the student's preferences for living with a roommate
        pass

    def viewStudents(self):
        #View a list of all students in the system
        pass

    def searchStudents(self, searchField: str):
        #Search for other students based on their name or student ID only
        pass