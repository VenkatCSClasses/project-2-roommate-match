import sqlite3

class Student:
    def __init__(self, id: int, name: str, email: str, password: str, hometown: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.hometown = hometown
        self.interests = []
        self.preferences = []
        self.requests = []
        self.groupID = -1  # No group assigned

    #Get methods
    def getID(self):
        #Return the student's ID
        
        return self.id

    def getName(self):
        #Return the student's name
        
        return self.name

    def getEmail(self):
        #Return the student's email
        
        return self.email

    def getPassword(self):
        #Return the student's password
        
        return self.password

    def getHometown(self):
        #Return the student's hometown
        
        return self.hometown



    def sendRequest(self, recipient, system):
        #Send a roommate request to another student using their student ID only
        pass

    def respondRequest(self, other_student, response: str):
        #Respond to a roommate request from another student with "accept" or "reject"
        pass

    def updatePassword(self, new_password: str):
        #Update the student's password
        
        if new_password == "":
            raise ValueError("Password cannot be empty")
        self.password = new_password

    def updateName(self, new_name: str):
        #Update the student's name
        
        if new_name == "":
            raise ValueError("Name cannot be empty")
        self.name = new_name

    def updateHometown(self, new_hometown: str):
        #Update the student's hometown
        
        self.hometown = new_hometown


    def updateInterests(self, db_path: str):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM interests")
        all_interests = cursor.fetchall()
        interest_map = {row[0]: row[1] for row in all_interests}

        print("\n--- Available Interests ---")
        for iid, title in interest_map.items():
            print(f"{iid}: {title}")

        while True:
            choice = input("\nEnter an interest ID to modify (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("Exiting interest update.")
                break

            if not choice.isdigit():
                print("Please enter a valid numeric ID.")
                continue

            interest_id = int(choice)

            if interest_id not in interest_map:
                print("Invalid interest ID. Try again.")
                continue

            interest_title = interest_map[interest_id]
            action = input(f"Do you want to add or remove '{interest_title}'? (add/remove): ").strip().lower()

            if action == "add":
                if interest_title in self.interests:
                    print(f"'{interest_title}' is already in your interests.")
                else:
                    self.interests.append(interest_title)
                    print(f"Added '{interest_title}' to your interests.")

            elif action == "remove":
                if interest_title in self.interests:
                    self.interests.remove(interest_title)
                    print(f"Removed '{interest_title}' from your interests.")
                else:
                    print(f"'{interest_title}' is not in your interests.")

            else:
                print("Invalid action. Type 'add' or 'remove'.")

        conn.close()


    def updatePreferences(self, new_preferences: list):
        #Update the student's preferences for living with a roommate
        pass

    def viewStudents(self):
        #View a list of all students in the system
        pass

    def searchStudents(self, searchField: str):
        #Search for other students based on their name or student ID only
        pass