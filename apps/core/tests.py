from django.test import TestCase
from django.urls import reverse

class CoreViewsTests(TestCase):
    def test_landing_status_code(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Navigate Your")

    def test_signin_status_code(self):
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")

    def test_signup_status_code(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_dashboard_status_code(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_logout_link(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')
        self.assertContains(response, reverse('landing'))

    def test_system_status_code(self):
        response = self.client.get(reverse('system_status'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System Status")
        self.assertContains(response, "Service Health Overview")

    def test_global_search_exact_course_code(self):
        from academics.models import Course
        Course.objects.create(course_code="LAWM305", title="Law Course")
        response = self.client.get(reverse('global_search') + "?q=LAWM305")
        self.assertRedirects(response, reverse('course_detail', kwargs={'course_code': 'LAWM305'}), fetch_redirect_response=False)

    def test_global_search_course_title(self):
        from academics.models import Course
        Course.objects.create(course_code="PSYC101", title="Biological Psychology")
        response = self.client.get(reverse('global_search') + "?q=Biological Psychology")
        self.assertRedirects(response, reverse('course_detail', kwargs={'course_code': 'PSYC101'}), fetch_redirect_response=False)

    def test_global_search_academic_rule(self):
        response = self.client.get(reverse('global_search') + "?q=minimum attendance")
        self.assertRedirects(response, reverse('advisor_chat') + "?q=minimum attendance", fetch_redirect_response=False)

    def test_global_search_natural_language(self):
        response = self.client.get(reverse('global_search') + "?q=What CGPA is required for progression to Year 2?")
        self.assertRedirects(response, reverse('advisor_chat') + "?q=What CGPA is required for progression to Year 2?", fetch_redirect_response=False)

    def test_global_search_greeting(self):
        response = self.client.get(reverse('global_search') + "?q=hi")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello!")

    def test_global_search_non_academic(self):
        response = self.client.get(reverse('global_search') + "?q=what is the weather")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "I can only answer questions related to the university's academic policies")

    def test_global_search_empty(self):
        response = self.client.get(reverse('global_search') + "?q=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No matching academic information found")

    def test_global_search_preserves_student_context(self):
        from academics.models import Course
        Course.objects.create(course_code="TEST101", title="Test Course")
        response = self.client.get(reverse('global_search') + "?q=TEST101&student_id=STU123")
        self.assertRedirects(response, reverse('course_detail', kwargs={'course_code': 'TEST101'}) + "?student_id=STU123", fetch_redirect_response=False)
