"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()


        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        # self.testuser_id = 8989
        # self.testuser.id = self.testuser_id                            

        self.client = app.test_client()

        db.session.commit()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_add_message_logged_out(self):
        """Can use add a message when logged out?"""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)        

    def test_delete_message(self):
        """Can you delete a message?"""

        msg = Message(id=1, user_id=self.testuser.id, text="This is a test!")
        
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp2 = c.post(f"/messages/1/delete")
            m = Message.query.get(1)

            self.assertEqual(resp2.status_code, 302)
            self.assertIsNone(m)


    def test_delete_message_logged_out(self):
        """Can use delete a message when logged out?"""

        msg = Message(id=1, user_id=self.testuser.id, text="This is a test!")
        
        db.session.add(msg)
        db.session.commit()

        with self.client as c:

            resp = c.post("/messages/1/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)

            m = Message.query.get(1)

            self.assertIsNotNone(m)


    def test_show_message(self):
        """Tests view message view function"""

        msg = Message(id=1, user_id=self.testuser.id, text="This is a test!") 

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/messages/1") 
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="single-message">This is a test!</p>', html)    


    def test_unauthorized_delete_message(self):
        """Test whether a user can add message as other user."""

        testuser2 = User.signup("testuser2", "test2@test.com", "test_password", None)

        msg = Message(id=1, user_id=self.testuser.id, text="This is a test!")
        
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser2.id

        resp = c.post("/messages/1/delete", follow_redirects=True)

        m = Message.query.get(1)

        self.assertIsNone(m) 