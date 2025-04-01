import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from ihiapp.models import DataStructure, EconomicActivityType
from users.models import Company, User
from axes.signals import user_locked_out
from axes.models import AccessAttempt
from django.db.models.signals import pre_save

@receiver(post_save, sender=Company)
def create_economic_activity_types(sender, instance, created, **kwargs):
    if instance.batch_enabled:
        second_level_entities = map(lambda d: d.descendant, DataStructure.objects.filter(ancestor=instance.root_entity, depth=1))

        existing_names = set(EconomicActivityType.objects.filter(
            company=instance
        ).values_list('name', flat=True))

        new_entities = []
        for entity in second_level_entities:
            if entity.name not in existing_names:
                new_entities.append(EconomicActivityType(
                    company=instance,
                    name=entity.name,
                ))
        EconomicActivityType.objects.bulk_create(new_entities)

@receiver(user_locked_out)
def handle_user_locked_out(sender, request, username, **kwargs):
    # ユーザモデルでロック状態を管理するため、AXESのロック状態をユーザモデルに反映する
    try:
        user = User.objects.get(email=username)
        user.is_locked = True
        user.save()
    except User.DoesNotExist:
        pass

@receiver(pre_save, sender=User)
def unlock_user(sender, instance, **kwargs):
    # ユーザモデルでロックが解除された場合、AXESのログイン失敗回数をリセットする
    if instance.pk is not None:
        try:
            original = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if original.is_locked and not instance.is_locked:
            AccessAttempt.objects.filter(username=instance.email).delete()
