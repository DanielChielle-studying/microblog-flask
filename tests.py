import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='gabriel', email='gabriel@gmail.com')
        u.set_password('dog')
        self.assertFalse(u.check_password('cat'))
        self.assertTrue(u.check_password('dog'))

    def test_avatar(self):
        u = User(username='albano', email='albano@gmail.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/611f63affa321d011a5e5791149c5d56?d=identicon&s128'))
        
    def test_follow(self):
        u1 = User(username='gabriel', email='gabriel@gmail.com')
        u2 = User(username='albano', email='albano@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, 'albano')
        self.assertEqual(u2_followers[0].username, 'gabriel')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        u1 = User(username='douglas', email='douglas@gmail.com')
        u2 = User(username='raisa', email='raisa@gmail.com')
        u3 = User(username='eduardo', email='eduardo@gmail.com')
        u4 = User(username='yulia', email='yulia@gmail.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.now(timezone.utc)
        p1 = Post(body="post from douglas", author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from raisa", author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from eduardo", author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from yulia", author=u4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])
    
if __name__ == '__main__':
    unittest.main(verbosity=2)