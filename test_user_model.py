"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        user1 = User.signup("test_user1", "test1@test.com", "passord_hash_1", None)

        db.session.add(user1)
        db.session.commit()

        user2 = User.signup("test_user2", "test2@test.com", "passord_hash_2", None)

        db.session.add(user2)
        db.session.commit()

        u1 = User.query.get(1)       
        u2 = User.query.get(2)      

        self.u1 = u1 
        self.u2 = u2 

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.id, 3)
        self.assertEqual(u, '<User #3: testuser, test@test.com>')