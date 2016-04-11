from rest_framework import serializers
from .models import InnAccUser

class InnAccUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = InnAccUser

class InnAccTransactionSerializer(serializers.Serializer):
	class Meta:
		model = InnAccUser

	from_inn = serializers.CharField()
	to_inn = serializers.CharField()
	amount = serializers.FloatField()

	def validate_from_inn(self,value):
		try:
			q = self.Meta.model.objects.get(inn=value)
		except:
			raise serializers.ValidationError("from field invalid inn")
		return q

	def validate_to_inn(self,value):
		try:
			q = self.Meta.model.objects.filter(inn=value)
			if not any(q):
				raise serializers.ValidationError("to field invalid inn")
		except:
			raise serializers.ValidationError("to field invalid inn")
		return q

	def validate(self,data):
		user = data['from_inn']
		if user.account < data['amount']:
			raise serializers.ValidationError("insufficient funds")
		return data

	def create(self):
		id_list = []
		validated_data = dict(list(self.validated_data.items()))
		q = validated_data.get('to_inn')
		amount = validated_data.get('amount')
		from_inn = validated_data.get('from_inn')
		amount_each = amount / q.count()
		from_inn.account = from_inn.account - amount
		for inn in q:
			inn.account += amount_each
			inn.save()
			id_list.append(inn.id)
		from_inn.save()
		id_list.append(from_inn.id)
		return id_list

