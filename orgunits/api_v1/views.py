"""
Copyright 2020 ООО «Верме»
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from orgunits.api_v1.serializers import OrganizationSerializer
from orgunits.models import Organization
from wfm.views import TokenAuthMixin


class OrganizationViewSet(TokenAuthMixin, ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    @action(methods=["GET"], detail=True)
    def parents(self, request, *args, **kwargs):
        """
        Возвращает родителей запрашиваемой организации
        TODO: Написать два действия для ViewSet (parents и children), используя методы модели
        """
        org_instance = Organization.objects.get(pk=self.kwargs['pk'])
        parents = org_instance.parents()

        return Response(OrganizationSerializer(parents, many=True, read_only=True).data)

    @action(methods=["GET"], detail=True)
    def children(self, request, *args, **kwargs):
        org_instance = Organization.objects.get(pk=self.kwargs['pk'])
        children = org_instance.children(include_self=False)

        return Response(OrganizationSerializer(children, many=True, read_only=True).data)
