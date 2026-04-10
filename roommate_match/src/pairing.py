class pairing:
    def __init__(self, user1_id, user2_id, user3_id=None, user4_id=None):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user3_id = user3_id
        self.user4_id = user4_id

    def get_user1_id(self):
        return self.user1_id

    def get_user2_id(self):
        return self.user2_id
    
    def get_user3_id(self):
        return self.user3_id

    def get_user4_id(self):
        return self.user4_id