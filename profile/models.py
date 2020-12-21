from django.contrib.auth.models import Group, User
from django.db import models


class Role(Group):
    @classmethod
    def get_roles_for_user(cls, user):
        return cls.objects.filter(user=user)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, blank=True)
