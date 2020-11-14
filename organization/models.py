# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from users.models import User
from organization.consts import KSG_POSITIONS


class InternalGroup(models.Model):
    class Meta:
        default_related_name = 'groups'
        verbose_name_plural = 'Internal groups'

    class Type(models.TextChoices):
        """
        Making use of https://docs.djangoproject.com/en/3.1/ref/models/fields/#enumeration-types
        Denotes the internal group type, either a interest-group, e.g. KSG-iT, Påfyll etc. or an internal
        grouping, e.g. Lyche bar og Edgar
        """
        INTEREST_GROUP = "interest-group"
        INTERNAL_GROUP = "internal-group"

    name = models.CharField(unique=True, max_length=32)
    type = models.CharField(max_length=32, null=False, blank=False, choices=Type.choices)
    description = models.CharField(max_length=1024, blank=True, null=True)

    members = models.ManyToManyField(
        User,
        blank=True,
        related_name='internal_groups'  # The default django user model already has a `groups` related_name
        # so we have to make a custom one
    )

    def __str__(self):
        return "Group %s" % self.name

    def __repr__(self):
        return "Group(name=%s)" % self.name


class InternalGroupPosition(models.Model):
    """
    A position for an internal group, e.g. Hovmester
    """

    name = models.CharField(unique=True, choices=KSG_POSITIONS, max_length=32)

    description = models.CharField(max_length=1024, blank=True, null=True)

    holders = models.ManyToManyField(
        User,
        blank=True,
        related_name='positions'
    )

    def __str__(self):
        return "Position %s" % self.name

    def __repr__(self):
        return "Position(name=%s)" % self.name
