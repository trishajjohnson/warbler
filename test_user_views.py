"""User views tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()


        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
                                   
        self.testuser2 = User.signup(username="testuser2", email="testuser2@test.com", password="testuser2", image_url=None)

        self.client = app.test_client()

        db.session.commit()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_show_user_profile(self):
        """Tests whether signed in user can view profile."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{ self.testuser.id }')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h4 id="sidebar-username">@{self.testuser.username}</h4>', html)


    def test_view_user_following(self):
        """Tests user view of users they're following."""

        self.testuser.following.append(self.testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id


            resp = c.get(f'/users/{ self.testuser.id }/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<p>@testuser2</p>', html)


    def test_view_user_following_logged_out(self):
        """Tests user view of users they're following when logged out."""

        with self.client as c:

            resp = c.get(f'/users/{self.testuser.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)


    def test_view_user_follower(self):
        """Tests user view of user's followers."""

        self.testuser.followers.append(self.testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id


            resp = c.get(f'/users/{ self.testuser.id }/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<p>@testuser2</p>', html)

    def test_view_user_followers_logged_out(self):
        """Tests user view of user's followers when logged out."""

        with self.client as c:

            resp = c.get(f'/users/{self.testuser.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<div class="alert alert-danger">Access unauthorized.</div>', html)
