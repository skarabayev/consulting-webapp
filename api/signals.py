from django.db.models.signals import post_delete
from django.dispatch import receiver
from api.models import CaseType, EDocument


@receiver(post_delete, sender=CaseType)
@receiver(post_delete, sender=EDocument)
def delete_files(sender, instance, *args, **kwargs):
    if sender == CaseType:
        file_url = instance.case_script.file.name
        instance.case_script.storage.delete(file_url)
    elif sender == EDocument:
        file_url = instance.file.file.name
        instance.file.storage.delete(file_url)