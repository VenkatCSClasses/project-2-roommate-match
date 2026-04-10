class roommateRequest:
   
    def __init__(self, sender_id, receiver_id, status):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.status = status

    def accept_request(self):
        self.status = "accepted"

    def reject_request(self):
        self.status = "rejected"