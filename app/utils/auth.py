from flask_login import UserMixin


class AdminUser(UserMixin):
    def __init__(self, user_id="admin"):
        self.id = user_id

    @property
    def is_admin(self):
        return True
