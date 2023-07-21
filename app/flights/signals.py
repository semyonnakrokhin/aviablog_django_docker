import os
import shutil

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete, pre_delete
from .models import Airframe, TrackImage, Meal

from .models import UserTrip, Flight


@receiver(pre_save, sender=Airframe)
@receiver(pre_save, sender=TrackImage)
@receiver(pre_save, sender=Meal)
def delete_previous_photo(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if isinstance(old_instance, Airframe) and old_instance.photo != instance.photo:
                old_instance.photo.delete(save=False)
            elif isinstance(old_instance, TrackImage) and old_instance.track_img != instance.track_img:
                old_instance.track_img.delete(save=False)
            elif isinstance(old_instance, Meal) and old_instance.meal_photo != instance.meal_photo:
                old_instance.meal_photo.delete(save=False)
        except sender.DoesNotExist:
            pass

@receiver(post_delete, sender=Airframe)
@receiver(post_delete, sender=TrackImage)
@receiver(post_delete, sender=Meal)
def delete_image(sender, instance, **kwargs):
    # Удаляем изображение из файловой системы после удаления записи

    if isinstance(instance, Airframe):
        image_field = instance.photo
    elif isinstance(instance, TrackImage):
        image_field = instance.track_img
    elif isinstance(instance, Meal):
        image_field = instance.meal_photo

    if image_field:
        image_path = image_field.path
        if os.path.exists(image_path):
            os.remove(image_path)

        # Удаление папок рекурсивно, если они стали пустыми
        folder_path = os.path.dirname(image_path)


        while not os.listdir(folder_path):
            parent_folder = os.path.dirname(folder_path)

            os.rmdir(folder_path)

            folder_path = parent_folder
