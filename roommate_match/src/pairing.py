class pairing:
    def __init__(self, user1_id, user2_id, user1_accepted=None, user2_accepted=None):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user1_accepted = user1_accepted
        self.user2_accepted = user2_accepted

    def get_user1_id(self):
        return self.user1_id

    def get_user2_id(self):
        return self.user2_id
    
    def get_user3_id(self):
        return self.user2_id
    
    def get_user4_id(self):
        return self.user2_id