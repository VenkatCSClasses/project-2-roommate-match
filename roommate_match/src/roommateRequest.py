class roommateRequest:
   
    def __init__(self, sender_id, receiver_id):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.accepted = None

    def accept_request(self):
        self.accepted = True

    def reject_request(self):
        self.accepted = False