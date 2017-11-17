from django.db import models

from organization.models import Group
from users.models import User


class Schedule(models.Model):
    """
    The Schedule model contains the entire schedule for one type of shifts.
    I.e. all 'Bodaga'-shifts have one schedule, all 'Lyche kjøkken'-shifts have one schedule,
    and so on.
    """
    name = models.CharField(max_length=100)


class ShiftSlotGroup(models.Model):
    """
    The ShiftSlotGroup model represents a grouping of slots that are occurring at the same time.
    The reason this is interesting is that people who work at the same time might want to connect.
    And we also want to group them in presentational circumstances.
    """
    name = models.CharField(max_length=100)
    schedule = models.ForeignKey(Schedule, null=False, blank=False)


class ScheduleSlotType(models.Model):
    """
    This model represents a type of slot that can be employed in a schedules shifts.
    This would typically be values like "Hovmester", "Barsjef", etc.
    """
    name = models.CharField(max_length=100, null=False, blank=False)
    schedule = models.ForeignKey(Schedule, null=False, blank=False)

    # This model describes what type of role is associated with
    # the slot type. For instance is Hovmester a "funkevakt", and Barservitør a "gjengisvakt".
    # TODO: Add choices when the new organization branch is merged
    role = models.CharField(max_length=32)

    # This fields represents which groups will be used in an automatic generation
    # of a schedule
    standard_groups = models.ManyToManyField(Group, blank=True)


class ShiftSlot(models.Model):
    """
    The ShiftSlot model represents a shift that is due to be or is filled by a person.
    """
    start = models.DateTimeField(blank=False, null=False)
    end = models.DateTimeField(blank=False, null=False)

    type = models.ForeignKey(ScheduleSlotType, null=False, blank=False)
    group = models.ForeignKey(ShiftSlotGroup)


class Shift(models.Model):
    """
    The Shift model represents a shift-slot filled by
    a person.
    """
    user = models.ForeignKey(User, null=False, blank=False)
    slot = models.OneToOneField(ShiftSlot, null=False, blank=False, related_name='filled_shift')


class ScheduleTemplate(models.Model):
    """
    This model contains a template for a schedules standard week. A schedule may have
    several templates.
    """
    name = models.CharField(max_length=100)
    schedule = models.ForeignKey(Schedule, blank=False, null=False)


class ShiftSlotGroupTemplate(models.Model):
    """
    This model represents a template for a ShiftSlotGroup.

    The model contains some additional information over a ShiftSlot, namely the rules
    for when the shift slot is supposed to occur.
    """
    name = models.CharField(max_length=100)
    schedule_template = models.ForeignKey(ScheduleTemplate, blank=False, null=False)


class ShiftSlotDayRule(models.Model):
    """
    This model represents a rule for what days a ShiftSlotGroup can occur
    """
    DAY_RULES = (
        ('mo', 'Monday'),
        ('tu', 'Tuesday'),
        ('we', 'Wednesday'),
        ('th', 'Thursday'),
        ('fr', 'Friday'),
        ('sa', 'Saturday'),
        ('su', 'Sunday'),
        ('wk', 'Weekdays'),
        ('ed', 'Weekends'),  # Friday, Saturday
        ('fu', 'Full weekends'),  # Friday, Saturday, Sunday
    )
    rule = models.CharField(max_length=2, choices=DAY_RULES)
    shift_slot_template = models.ForeignKey(ShiftSlotGroupTemplate, related_name='day_rules')


class ShiftSlotTemplate(models.Model):
    """
    This model represents a template for a ShiftSlot.
    """
    start = models.DateTimeField(blank=False, null=False)
    end = models.DateTimeField(blank=False, null=False)

    type = models.ForeignKey(ScheduleSlotType, null=False, blank=False)
    group = models.ForeignKey(ShiftSlotGroupTemplate, null=False, blank=False)

