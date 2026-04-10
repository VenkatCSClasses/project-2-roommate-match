class roommateRequest:
   
    def __init__(self, sender_id, receiver_id):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.accepted = None

    def accept_request(self):
        self.accepted = True

    def reject_request(self):
        self.accepted = False

    def getStatus(self):
        return self.accepted
    
    def getSenderId(self):
        return self.sender_id
    
    def getReceiverId(self):   
        return self.receiver_id
    
    def __str__(self):
        return f"Roommate Request from {self.sender_id} to {self.receiver_id}, Accepted: {self.accepted}"   