from src.system import RoommateSystem

class pairing:
    def __init__(self, group_id, students):
        self.group_id = group_id
        self.students = students

    def get_group_id(self):
        return self.group_id

    def get_students(self):
        return self.students

    def finalize_pairing(self):
        for student in RoommateSystem.students:
            if student.id in self.students:
                student.groupID = self.group_id