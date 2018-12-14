import os,sys
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime, timedelta
import unittest
from app import create_app, db, app
from app.models import User, Post
import config as Config

class UserModelCase(unittest.TestCase):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    def setUp(self):
        self.db_uri = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='wangxiyang')
        u.set_password('wangxiyang')
        self.assertFalse(u.check_password('xiyang'))
        self.assertTrue(u.check_password('wangxiyang'))

    def test_follow(self):
        u1 = User(username='wangxiyang1', email='wangxiyang1@qq.com')
        u2 = User(username='wangxiyang', email='wangxiyang@qq.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'wangxiyang')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'wangxiyang1')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        u1 = User(username='wangxiyang1', email='wangxiyang1@qq.com')
        u2 = User(username='wangxiyang', email='wangxiyang@qq.com')
        u3 = User(username='wangxiyang2', email='wangxiyang2@qq.com')
        u4 = User(username='wangxiyang3', email='wangxiyang3@qq.com')
        db.session.add_all([u1, u2, u3, u4])


        time = datetime.utcnow()
        p1 = Post(body="post from wangxiyang1", author=u1,
                  timestamp=time+ timedelta(seconds=1))
        p2 = Post(body="post from wangxiyang", author=u2,
                  timestamp=time+ timedelta(seconds=4))
        p3 = Post(body="post from wangxiyang2", author=u3,
                  timestamp=time+ timedelta(seconds=3))
        p4 = Post(body="post from wangxiyang3", author=u4,
                  timestamp=time+ timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()


        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main()
