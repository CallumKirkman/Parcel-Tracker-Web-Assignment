from main import app
import unittest


class FlaskTestCase(unittest.TestCase):

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/home', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_product(self):
        tester = app.test_client(self)
        response = tester.get('/product', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_tracking(self):
        tester = app.test_client(self)
        response = tester.get('/tracking', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        tester = app.test_client(self)
        response = tester.get('/about', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_update_account(self):
        tester = app.test_client(self)
        response = tester.get('/update-account', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart(self):
        tester = app.test_client(self)
        response = tester.get('/add-to-cart', content_type='html/text')
        self.assertEqual(response.status_code, 405)

    def test_login(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    def test_signup(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        tester = app.test_client(self)
        response = tester.get('/logout', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    def test_error(self):
        tester = app.test_client(self)
        response = tester.get('/error', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # def test_account(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/account', content_type='html/text')
    #     self.assertEqual(response.status_code, 200)

    # def test_delete_account(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/delete-account', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)
    # def test_checkout(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/checkout', content_type='html/text')
    #     self.assertEqual(response.status_code, 200)

    # def test_create_order(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/create-order', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)

    # def test_empty(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/empty', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
