from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    Product,
    QuizQuestion,
    ShortAnswerQuestion,
)


class LearningSiteTests(TestCase):
    def test_homepage_shows_learning_content_and_quiz(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indian Logic and')
        self.assertNotContains(response, 'Mapping of Pramāṇas and Computing Concepts')
        self.assertNotContains(response, 'Test Your Understanding')
        self.assertContains(response, 'The Five-Part Nyāya Argument')
        self.assertContains(response, 'href="/relation/"')
        self.assertContains(response, 'href="/questions/"')

    def test_relation_navigation_opens_only_relation_page(self):
        response = self.client.get(reverse('relation'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relation Between')
        self.assertContains(response, 'Mapping of Pramāṇas and Computing Concepts')
        self.assertNotContains(response, 'Test Your Understanding')
        self.assertContains(response, 'aria-current="page">Relation</a>')

    def test_questions_navigation_opens_only_quiz_page(self):
        response = self.client.get(reverse('questions'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Your Understanding')
        self.assertContains(response, 'Short Answer Questions')
        self.assertNotContains(response, 'The Six Systems of Indian Philosophy')
        self.assertNotContains(response, 'Mapping of Pramāṇas and Computing Concepts')
        self.assertContains(response, 'aria-current="page">Questions</a>')

    def test_quiz_matches_reference_topics(self):
        response = self.client.get(reverse('questions'))

        self.assertContains(
            response,
            'Which of the following is a means of valid knowledge',
        )
        self.assertContains(
            response,
            'What is the main focus of Vaiśeṣika philosophy?',
        )
        self.assertContains(
            response,
            'According to V. S. Sarma, what can be compared with pratyakṣa',
        )

    def test_quiz_scores_answers_on_the_server(self):
        questions = list(QuizQuestion.objects.all())
        response = self.client.post(reverse('questions'), {
            f'question_{question.pk}': str(question.correct_option)
            for question in questions
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['quiz_result']['score'], len(questions))
        self.assertEqual(response.context['quiz_result']['percent'], 100)

    def test_quiz_rejects_missing_answers(self):
        question = QuizQuestion.objects.first()
        response = self.client.post(reverse('questions'), {
            f'question_{question.pk}': str(question.correct_option),
        })

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['quiz_result'])
        self.assertContains(response, 'Please choose an answer for every question.')

    def test_short_answer_quiz_scores_case_insensitively(self):
        questions = list(ShortAnswerQuestion.objects.all())
        response = self.client.post(reverse('questions'), {
            'quiz_type': 'short-answer',
            f'question_{questions[0].pk}': 'anumana',
            f'question_{questions[1].pk}': 'udaharana',
            f'question_{questions[2].pk}': 'INFERENCE ENGINE',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['quiz_result']['score'], len(questions))
        self.assertEqual(response.context['quiz_mode'], 'short-answer')
        self.assertContains(response, 'You got 3 out of 3 right.')

    def test_short_answer_quiz_rejects_missing_answers(self):
        question = ShortAnswerQuestion.objects.first()
        response = self.client.post(reverse('questions'), {
            'quiz_type': 'short-answer',
            f'question_{question.pk}': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['quiz_result'])
        self.assertContains(response, 'Please answer every question.')

    def test_invalid_quiz_mode_is_rejected(self):
        response = self.client.post(reverse('questions'), {'quiz_type': 'unknown'})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['quiz_result'])
        self.assertContains(response, 'Choose a quiz format and try again.')

    def test_shop_is_available_at_shop_path(self):
        response = self.client.get(reverse('shop:product_list'))

        self.assertEqual(response.status_code, 200)


class LearningAccountTests(TestCase):
    def test_learning_navigation_links_to_account_pages(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'href="/login/">Log in</a>')
        self.assertContains(response, 'href="/signup/">Sign up</a>')

        user = User.objects.create_user(username='learner', password='safe-password')
        self.client.force_login(user)
        authenticated_response = self.client.get(reverse('home'))
        self.assertContains(authenticated_response, 'action="/logout/"')
        self.assertContains(authenticated_response, 'Sign out</button>')

    def test_account_pages_render_with_learning_navigation(self):
        login_response = self.client.get(reverse('account_login'))
        signup_response = self.client.get(reverse('account_signup'))

        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, 'Good to see')
        self.assertContains(login_response, 'name="username"')
        self.assertContains(login_response, 'name="password"')
        self.assertEqual(signup_response.status_code, 200)
        self.assertContains(signup_response, 'Create your')
        self.assertContains(signup_response, 'name="email"')
        self.assertContains(signup_response, 'name="password1"')
        self.assertContains(signup_response, 'logic-orb')

    def test_signup_creates_user_and_starts_authenticated_session(self):
        response = self.client.post(reverse('account_signup'), {
            'username': 'new-learner',
            'email': 'learner@example.com',
            'password1': 'Another-safe-pass-123',
            'password2': 'Another-safe-pass-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='new-learner').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('account_signup'), {
            'username': 'new-learner',
            'email': 'learner@example.com',
            'password1': 'Another-safe-pass-123',
            'password2': 'Different-safe-pass-123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='new-learner').exists())
        self.assertContains(response, 'The two password fields didn’t match.')

    def test_login_authenticates_and_returns_to_learning_home(self):
        User.objects.create_user(
            username='learner',
            password='Another-safe-pass-123',
        )

        response = self.client.post(reverse('account_login'), {
            'username': 'learner',
            'password': 'Another-safe-pass-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_preserves_safe_next_destination(self):
        User.objects.create_user(
            username='learner',
            password='Another-safe-pass-123',
        )
        destination = reverse('questions')

        response = self.client.post(
            f'{reverse("account_login")}?next={destination}',
            {
                'username': 'learner',
                'password': 'Another-safe-pass-123',
                'next': destination,
            },
        )

        self.assertRedirects(response, destination)

    def test_logout_returns_to_learning_home(self):
        user = User.objects.create_user(
            username='learner',
            password='Another-safe-pass-123',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('account_logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)


class ShopTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            password='safe-test-password',
            email='customer@example.com',
        )
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            category=self.category,
            name='Django Basics',
            slug='django-basics',
            price=Decimal('12.50'),
            stock=5,
        )

    def test_store_lists_active_in_stock_products(self):
        response = self.client.get(reverse('shop:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Basics')

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'new-customer',
            'email': 'new@example.com',
            'password1': 'Another-safe-pass-123',
            'password2': 'Another-safe-pass-123',
        })

        self.assertRedirects(response, reverse('shop:product_list'))
        self.assertTrue(User.objects.filter(username='new-customer').exists())
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_add_to_cart_requires_login_then_adds_item(self):
        response = self.client.post(
            reverse('shop:add_to_cart', args=[self.product.pk]),
        )
        self.assertRedirects(
            response,
            f'{reverse("shop:login")}?next={reverse("shop:add_to_cart", args=[self.product.pk])}',
        )

        self.client.login(username='customer', password='safe-test-password')
        response = self.client.post(
            reverse('shop:add_to_cart', args=[self.product.pk]),
        )

        self.assertRedirects(response, reverse('shop:cart'))
        self.assertEqual(CartItem.objects.get().quantity, 1)

    def test_checkout_creates_order_and_decrements_stock(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.login(username='customer', password='safe-test-password')

        response = self.client.post(reverse('shop:checkout'), {
            'full_name': 'Test Customer',
            'address_line_1': '1 Main Street',
            'address_line_2': '',
            'city': 'Example City',
            'postal_code': '12345',
            'country': 'Example Country',
        })

        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse('shop:order_detail', args=[order.pk]))
        self.assertEqual(order.total, Decimal('25.00'))
        self.assertEqual(order.items.get().quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(cart.items.exists())

    def test_checkout_rejects_quantity_above_stock_without_order(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=6)
        self.client.login(username='customer', password='safe-test-password')

        response = self.client.post(reverse('shop:checkout'), {
            'full_name': 'Test Customer',
            'address_line_1': '1 Main Street',
            'address_line_2': '',
            'city': 'Example City',
            'postal_code': '12345',
            'country': 'Example Country',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
