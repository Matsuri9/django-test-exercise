from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime
from todo.models import Task

class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['uncompleted_tasks']), 0)
        self.assertEqual(len(response.context['completed_tasks']), 0)
    
    def test_index_post(self):
        client = Client()
        data = {'title': 'Test Task', 'due_at': '2024-06-30T23:59:59', 'priority': '5'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 302)  # リダイレクトを期待
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['uncompleted_tasks']), 1)
        self.assertEqual(len(response.context['completed_tasks']), 0)
    
    def test_index_get_order_post(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertIn(task1, response.context['uncompleted_tasks'])
        self.assertIn(task2, response.context['uncompleted_tasks'])

    def test_index_get_order_due(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['uncompleted_tasks'][0], task1)
        self.assertEqual(response.context['uncompleted_tasks'][1], task2)
    
    def test_index_get_order_priority(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)), priority=1)
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 7, 1)), priority=2)
        task2.save()
        client = Client()
        response = client.get('/?order=priority')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['uncompleted_tasks'][0], task2)
        self.assertEqual(response.context['uncompleted_tasks'][1], task1)

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)
    
    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)
