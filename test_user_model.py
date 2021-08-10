"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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
    """Test functions of User model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

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
        # self.assertEqual(u, '<User #3: testuser, test@test.com>')


    ###########################
    #                         #
    #   testing following     #
    #                         #
    ###########################

    def test_is_following(self):
        """Testing when user1 is_following user2."""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))


        self.u1.following.remove(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 0)
        self.assertEqual(len(self.u1.following), 0)


    def test_is_followed_by(self):
        """Testing when user1 is_followed_by user2."""

        self.u1.followers.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 1)
        self.assertEqual(len(self.u2.following), 1)
        self.assertTrue(self.u1.is_followed_by(self.u2))

        self.u1.followers.remove(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.following), 0)
        self.assertFalse(self.u1.is_followed_by(self.u2))


    ###########################
    #                         #
    #   testing creating      #
    #       new user          #
    #                         #
    ###########################

    def test_user_create(self):
        """Tests whether new user is created."""

        new_user = User.signup("test_new_user", "testing@test.com", "this_has_password", None)
        new_user.id = 999
        db.session.commit()

        new_u = User.query.get(999)

        self.assertEqual(new_u.id, 999)
        self.assertIsNotNone(new_u)
        self.assertEqual(new_u.email, "testing@test.com")

    def test_create_user_invalid_username(self):
        """Tests create user when invalid username is provided."""

        new_user = User.signup(None, "test@test.com", "this_has_password", None)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_create_user_invalid_email(self):
        """Tests create user when invalid email is provided."""

        new_user2 = User.signup("testuser2", None, "this_has_password", None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_create_user_invalid_password(self):
        """Tests create user when invalid password is provided."""

        with self.assertRaises(ValueError) as context:
            User.signup("testuser3", "test3@test.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testuser3", "test3@test.com", None, None)



    ########################
    #                      #
    # Authentication Tests #
    #                      #
    ########################

    def test_user_auth(self):
        """Testing whether User.authenticate works."""

        user = User.authenticate(username=self.u1.username, password="passord_hash_1")
        wrong_username = User.authenticate(username="wrong_username", password="passord_hash_1")
        wrong_password = User.authenticate(username=self.u2.username, password="wrong_password")
        
        self.assertTrue(user)
        self.assertFalse(wrong_username)
        self.assertFalse(wrong_password)

