class roommateRequest:
   
    def __init__(self, sender_id, receiver1_id, receiver2_id=None, receiver3_id=None):
        self.sender_id = sender_id
        self.receiver1_id = receiver1_id
        self.receiver2_id = receiver2_id
        self.receiver3_id = receiver3_id
        self.accepted = None

    def accept_request(self):
        self.accepted = True

    def reject_request(self):
        self.accepted = False

    def getStatus(self):
        return self.accepted
    
    def getSenderId(self):
        return self.sender_id
    
    def getReceiver1Id(self):
        return self.receiver1_id

    def getReceiver2Id(self):
        return self.receiver2_id

    def getReceiver3Id(self):
        return self.receiver3_id