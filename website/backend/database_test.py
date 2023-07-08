import unittest
from database import get_session, open_or_create_db, register_user, User, get_user_by_email


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.engine = open_or_create_db('sqlite:///:memory:')

    def test_register_user(self):
        # Add an email
        test_email = "test@test.com"
        register_user(test_email)

        # Check if the email was added
        with get_session() as session:
            email_in_db = session.query(User).filter_by(email=test_email).first()
            self.assertIsNotNone(email_in_db, "Email should be in database")
            self.assertEqual(email_in_db.email, test_email, "Email in database should match the test email")

        # Check if get user can find the email
        res = get_user_by_email(test_email)
        self.assertIsNotNone(res, "Email should be in database")
        self.assertEqual(res.email, test_email, "Email in database should match the test email")

if __name__ == '__main__':
    unittest.main()
