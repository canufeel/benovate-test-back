from django.test import TestCase
from django.contrib.auth.models import User
from .models import InnAccUser
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy
import json

class TestModel(TestCase):

	def test_user_creation_triggers_inn_acc_creation(self):
		self.assertEqual(User.objects.count(),0)
		self.assertEqual(InnAccUser.objects.count(),0)
		user = User.objects.create(**{'username':'test',
			'password':'test'})
		self.assertEqual(User.objects.count(),1)
		self.assertEqual(InnAccUser.objects.count(),1)

	def test_can_create_innacc_without_user(self):
		innacc = InnAccUser.objects.create(**{
			'account': 62.22,
			'inn': '55452'
			})
		self.assertEqual(InnAccUser.objects.count(),1)

class TestUserEndPoint(APITestCase):
	def setUp(self):
		self.url = '/api/innaccuser'

	def test_get_list(self):
		response = self.client.get(self.url,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_200_OK)

	def test_post_details(self):
		data = {
			'account': 62.22,
			'inn': '55452'
			}
		response = self.client.post(self.url, data,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_201_CREATED)
		self.assertEqual(InnAccUser.objects.count(),1)

	def test_put(self):
		innacc = InnAccUser.objects.create(**{
			'account': 62.22,
			'inn': '55452'
			})
		url = self.url + '/' + str(innacc.id)
		new_inn = '95052'
		data = {
			'account': 62.22,
			'inn': new_inn
			}
		response = self.client.put(url, data,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_200_OK)
		innacc = InnAccUser.objects.get(id=innacc.id)
		self.assertEqual(innacc.inn,new_inn)

	def test_endpoint_supports_inn_filtering(self):
		inn1 = '55452'
		inn2 = '22222'
		inn3 = '33333'
		innacc = InnAccUser.objects.create(**{
			'account': 62.22,
			'inn': inn1
			})
		innacc2 = InnAccUser.objects.create(**{
			'account': 62.22,
			'inn': inn2
			})
		innacc3 = InnAccUser.objects.create(**{
			'account': 62.22,
			'inn': inn3
			})
		url = self.url + '?query=22'
		response = self.client.get(url,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_200_OK)
		json_lst = json.loads(response.content.decode('utf-8'))
		self.assertEqual(len(json_lst),1)
		self.assertEqual(json_lst[0]['id'],innacc2.id)

class TestTransactionEndPoint(APITestCase):

	def setUp(self):
		self.url = '/api/transaction'
		self.model = InnAccUser
		self.user1 = InnAccUser.objects.create(**{"account":100,
			"inn":"abc"})
		self.user2 = InnAccUser.objects.create(**{"account":200,
			"inn":"def"})
		self.user3 = InnAccUser.objects.create(**{"account":300,
			"inn":"ghi"})
		self.user4 = InnAccUser.objects.create(**{"account":500,
			"inn":"jkl"})
		self.user5 = InnAccUser.objects.create(**{"account":100,
			"inn":"ghi"})
		self.user6 = InnAccUser.objects.create(**{"account":100,
			"inn":"jkl"})

	def test_basic_transaction(self):
		data = {
			'from_inn':self.user1.inn,
			'to_inn':self.user2.inn,
			'amount':100
		}
		response = self.client.post(self.url, data,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_200_OK)
		self.user1 = self.model.objects.get(id=self.user1.id)
		self.user2 = self.model.objects.get(id=self.user2.id)
		self.assertEqual(self.user1.account,0)
		self.assertEqual(self.user2.account,300.00)

	def test_multiple_transaction(self):
		data = {
			'from_inn':self.user1.inn,
			'to_inn':self.user3.inn,
			'amount':100
			}
		response = self.client.post(self.url, data,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_200_OK)
		self.user1 = self.model.objects.get(id=self.user1.id)
		self.user3 = self.model.objects.get(id=self.user3.id)
		self.user5 = self.model.objects.get(id=self.user5.id)
		self.assertEqual(self.user1.account,0)
		self.assertEqual(self.user3.account,350.00)
		self.assertEqual(self.user5.account,150.00)

	def test_wrong_inn_transaction(self):
		data = {
			'from_inn':self.user1.inn,
			'to_inn':'wrong_inn',
			'amount':100
			}
		response = self.client.post(self.url, data,
			format='json')
		self.assertEqual(response.status_code,
			status.HTTP_400_BAD_REQUEST)

	def test_not_enougth_funds(self):
		data = {
			'from_inn':self.user1.inn,
			'to_inn':self.user3.inn,
			'amount':500
			}
		response = self.client.post(self.url, data,
			format='json')
		self.user1 = self.model.objects.get(id=self.user1.id)
		self.user3 = self.model.objects.get(id=self.user3.id)
		self.assertEqual(response.status_code,
			status.HTTP_400_BAD_REQUEST)
