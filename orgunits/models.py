"""
Copyright 2020 ООО «Верме»
"""

from django.db import models
from django.db.models.expressions import RawSQL


class OrganizationQuerySet(models.QuerySet):
    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """

        return self.filter(id__in=RawSQL(
            '''WITH tblChild AS
          (
              SELECT orgunits_organization.id
              FROM orgunits_organization
              WHERE parent_id = %s
              UNION ALL
              SELECT orgunits_organization.id
              FROM orgunits_organization
                       JOIN tblChild ON orgunits_organization.parent_id = tblChild.id
          )
         SELECT *
         FROM 
         (
          SELECT orgunits_organization.id
          FROM orgunits_organization
          WHERE id = %s
          UNION ALL
          SELECT *
          FROM tblChild
         )''', [root_org_id, root_org_id]))

    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """
        return self.filter(id__in=RawSQL(
            '''WITH tblParent AS
         (
             SELECT orgunits_organization.parent_id
             FROM orgunits_organization
             WHERE id =%s
             UNION ALL
             SELECT orgunits_organization.parent_id
             FROM orgunits_organization
                      JOIN tblParent ON orgunits_organization.id = tblParent.parent_id
         )
        SELECT *
        FROM 
        (
            SELECT orgunits_organization.id
            FROM orgunits_organization
            WHERE id = %s
            UNION ALL
            SELECT *
            FROM tblParent
        )
            ''', [child_org_id, child_org_id]))


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организация"
        verbose_name = "Организации"

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """

        return OrganizationQuerySet(Organization).tree_upwards(self.pk).exclude(pk=self.pk)

    def children(self, include_self=True):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """

        children = OrganizationQuerySet(Organization).tree_downwards(self.pk)
        if not include_self:
            return children.exclude(pk=self.pk)
        return children

    def __str__(self):
        return self.name
