import sqlite3

from roommate_match.src.roommateRequest import roommateRequest

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



    def sendRequest(self, receiver_ids, system):
        #Send a roommate request to another student using their student ID only
        
        if self.groupID != -1:
            raise Exception("You are already in a group.")

        for req in system.requests:
            if req.sender_id == self.studentID:
                raise Exception("You already have a active request.")

        if len(receiver_ids) < 1 or len(receiver_ids) > 3:
            raise Exception("You must invite between 1 and 3 students.")

        for rid in receiver_ids:
            receiver = system.getStudentByID(rid)

            if receiver is None:
                raise Exception(f"Student {rid} does not exist.")

            if receiver.groupID != -1:
                raise Exception(f"Student {rid} is already in a group.")

            for req in system.requests:
                if rid in req.receiver_ids:
                    raise Exception(f"Student {rid} already has a pending request.")

            new_request = roommateRequest(self.studentID, receiver_ids)

            system.requests.append(new_request)

    

    def respondRequest(self, request_id, accept, system):
        #Respond to a roommate request from another student with "accept" or "reject"
        
        req = None
        for r in system.requests:
            if r.request_id == request_id:
                req = r
                break

        if req is None:
            raise Exception("Request not found.")

        req.responses[self.studentID] = accept

        if False in req.responses.values():
            system.requests.remove(req)
            return

        if all(v is True for v in req.responses.values()):
            system.updateRequestList(req)
            system.requests.remove(req)
            

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
                    cursor.execute(
                        "INSERT INTO students_to_interest (student_id, interest_id) VALUES (?, ?)",
                        (self.id, interest_id)
                    )
                    conn.commit()
                    print(f"Added '{interest_title}' to your interests.")

            elif action == "remove":
                if interest_title in self.interests:
                    self.interests.remove(interest_title)
                    cursor.execute(
                        "DELETE FROM students_to_interest WHERE student_id = ? AND interest_id = ?",
                        (self.id, interest_id)
                    )
                    conn.commit()
                    print(f"Removed '{interest_title}' from your interests.")
                else:
                    print(f"'{interest_title}' is not in your interests.")

            else:
                print("Invalid action. Type 'add' or 'remove'.")

        conn.close()


    def updatePreferences(self, db_path: str):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM preferences")
        all_preferences = cursor.fetchall()
        preference_map = {row[0]: row[1] for row in all_preferences}

        print("\n--- Available Preferences ---")
        for pid, title in preference_map.items():
            print(f"{pid}: {title}")

        while True:
            choice = input("\nEnter a preference ID to modify (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("Exiting preference update.")
                break

            if not choice.isdigit():
                print("Please enter a valid numeric ID.")
                continue

            preference_id = int(choice)

            if preference_id not in preference_map:
                print("Invalid preference ID. Try again.")
                continue

            preference_title = preference_map[preference_id]
            action = input(f"Do you want to add or remove '{preference_title}'? (add/remove): ").strip().lower()

            if action == "add":
                if preference_title in self.preferences:
                    print(f"'{preference_title}' is already in your preferences.")
                else:
                    self.preferences.append(preference_title)
                    cursor.execute(
                        "INSERT INTO students_to_preference (student_id, preference_id) VALUES (?, ?)",
                        (self.id, preference_id)
                    )
                    conn.commit()
                    print(f"Added '{preference_title}' to your preferences.")

            elif action == "remove":
                if preference_title in self.preferences:
                    self.preferences.remove(preference_title)
                    cursor.execute(
                        "DELETE FROM students_to_preference WHERE student_id = ? AND preference_id = ?",
                        (self.id, preference_id)
                    )
                    conn.commit()
                    print(f"Removed '{preference_title}' from your preferences.")
                else:
                    print(f"'{preference_title}' is not in your preferences.")

            else:
                print("Invalid action. Type 'add' or 'remove'.")

        conn.close()




    def viewStudents(self):
        #View a list of all students in the system
        
        return self.students

    def searchStudents(self, searchField, system):
        if not searchField.isdigit():
            raise ValueError("Search must be by numeric student ID only")

        target_id = int(searchField)

        for student in system.students:
            if student.id == target_id:
                return student

        raise ValueError("Student not found")


    def rankStudentsByMatch(self, allStudents):
        ranked = []

        for other in allStudents:
            if other.id == self.id:
                continue

            interestMatches = len(set(self.interests) & set(other.interests))
            preferenceMatches = len(set(self.preferences) & set(other.preferences))
            totalScore = interestMatches + preferenceMatches

            ranked.append((totalScore, other))

        ranked.sort(key=lambda x: x[0], reverse=True)

        return [student for score, student in ranked]



