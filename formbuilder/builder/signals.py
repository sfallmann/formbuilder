from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from .models import FieldTemplate, FieldTemplateOptions
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=FieldTemplate)
def create_options_for_new_fieldtemplate(sender, created, instance, **kwargs):

    if created:

        options = FieldTemplateOptions(field_template=instance)
        options.save()

        msg = "FieldTemplateOptions [id:%s] created"\
        "for FieldTemplate [id:%s].\n\r" % (instance.pk, options.pk)

        logger.info(msg)


@receiver(pre_save, sender=FieldTemplate)
def set_field_template_position_save(sender, instance, **kwargs):




    if instance.pk is None:

        all_fields = FieldTemplate.objects.filter(
            form_template=instance.form_template, field_set=None)
        instance.position = all_fields.count() + 1

    else:

        orig = FieldTemplate.objects.get(pk=instance.pk)

        if instance.field_set != orig.field_set:
            count = FieldTemplate.objects.filter(
                form_template=instance.form_template, field_set=instance.field_set)

            instance.position = all_fields.count() + 1

            all_fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=orig.field_set,
                position__gt=orig.position
            )
            for field in all_fields:
                FieldTemplate.objects.filter(
                    pk=field.pk).update(position=field.position-1)
        else:
            if instance.position != orig.position:

                if FieldTemplate.objects.filter(position=instance.position):

                    obj_at_position = FieldTemplate.objects.get(position=instance.position)
                    FieldTemplate.objects.filter(
                        pk=obj_at_position.pk).update(position=orig.position)


@receiver(post_delete, sender=FieldTemplate)
def set_field_template_position_delete(sender, instance, **kwargs):

    all_fields = FieldTemplate.objects.filter(
        form_template=instance.form_template,
        field_set=instance.field_set,
        position__gt=instance.position
    ).order_by('position')

    for field in all_fields:
        FieldTemplate.objects.filter(
            pk=field.pk).update(position=field.position-1)

