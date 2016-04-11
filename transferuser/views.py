from rest_framework import viewsets
from rest_framework import generics
from .models import InnAccUser
from .serializers import (InnAccUserSerializer,
	InnAccTransactionSerializer)
from rest_framework.response import Response
from rest_framework import status

class InnAccUserViewSet(viewsets.ModelViewSet):
	queryset = InnAccUser.objects.all()
	serializer_class = InnAccUserSerializer

	def get_queryset(self):
		queryset = InnAccUser.objects.all()
		query = self.request.query_params.get('query', None)
		if query is not None:
			queryset = queryset.filter(inn__icontains=query)
		return queryset

class TransactionView(generics.CreateAPIView):
	queryset = InnAccUser.objects.all()
	serializer_class = InnAccTransactionSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer2 = self.perform_create(serializer)
		headers = self.get_success_headers(serializer2.data)
		return Response(serializer2.data, status=status.HTTP_200_OK, headers=headers)

	def perform_create(self,serializer):
		instance_ids_list = serializer.create()
		queryset = self.queryset.filter(id__in=instance_ids_list)
		serializer2 = InnAccUserSerializer(queryset, many=True)
		return serializer2



