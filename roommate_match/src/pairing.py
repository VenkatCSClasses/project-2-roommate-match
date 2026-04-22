class pairing:
    def __init__(self, group_id, students):
        self.group_id = group_id
        self.students = students
        self.group = students

    def get_group_id(self):
        return self.group_id

    def get_students(self):
        return self.students

    # def finalize_pairing(self):
    #     for student in RoommateSystem.students:
    #         if student.id in self.students:
    #             student.groupID = self.group_id

    def requestToPairing(self, request):
        group = [request.sender_id] + request.receiver_ids
        new_pairing = pairing(self.generateGroupId(), group)
        self.pairings.append(new_pairing)
        if request in self.requests:
            self.requests.remove(request)
        return self.students
