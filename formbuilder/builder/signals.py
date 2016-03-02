from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
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

    print kwargs
    print "in save\n\n\n"

    if instance.pk is None:

        all_fields = FieldTemplate.objects.filter(
            form_template=instance.form_template, field_set=None)
        instance.position = all_fields.count() + 1

    else:

        all_fields = FieldTemplate.objects.filter(
            form_template=instance.form_template,
            field_set=instance.field_set
        )

        orig = FieldTemplate.objects.get(pk=instance.pk)

        if instance.field_set == orig.field_set:

            for field in all_fields:

                if instance.position == field.position:

                    if instance.pk != field.pk:

                        FieldTemplate.objects.filter(
                            pk=field.pk).update(position=orig.position)

                        break;

        else:

            instance.position = all_fields.count() + 1

            all_fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set,
                position__gt=orig.position
            )
            for field in all_fields:
                FieldTemplate.objects.filter(
                    pk=field.pk).update(position=field.position-1)


@receiver(post_delete, sender=FieldTemplate)
def set_field_template_position_delete(sender, instance, **kwargs):

    print kwargs
    print "in delete\n\n\n"

    all_fields = FieldTemplate.objects.filter(
        form_template=instance.form_template,
        field_set=instance.field_set,
        position__gt=instance.position
    )

    for field in all_fields:
        FieldTemplate.objects.filter(
            pk=field.pk).update(position=field.position)


