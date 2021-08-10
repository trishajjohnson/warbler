"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Tests functions of Message model."""

    def setUp(self):
        """Creates test user for testing messages."""

        db.drop_all()
        db.create_all()

        test_user = User.signup("test_user1", "test1@test.com", "passord_hash_1", None)

        db.session.add(test_user)
        db.session.commit()

        self.test_user = User.query.get(test_user.id)

        self.client = app.test_client()

    def tearDown(self):

        db.session.rollback()
        return super().tearDown()

    def test_new_message(self):
        """Tests if message was created and added to DB."""

        msg = Message(user_id=self.test_user.id, text="This is a test!")

        db.session.add(msg)
        db.session.commit()

        msg = Message.query.get(self.test_user.id)

        self.assertEqual(self.test_user.messages[0].text, "This is a test!")
        self.assertEqual(len(self.test_user.messages), 1)

    def test_likes(self):

        new_msg = Message(user_id=self.test_user.id, text="This is a test!")
        test_user2 = User.signup("test_user2", "test2@test.com", "passord_hash_2", None) 
        db.session.add_all([new_msg, test_user2])
        db.session.commit()

        test_user2.likes.append(new_msg)

        db.session.commit()

        self.assertEqual(len(test_user2.likes), 1)

