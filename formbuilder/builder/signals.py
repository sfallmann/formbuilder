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

        fields = FieldTemplate.objects.filter(
            form_template=instance.form_template, field_set=None)
        instance.position = fields.count() + 1

        msg = "New FieldTemplate. Set to "\
        "position [%s], field_set [id:%s], form_template [id:%s]"\
        ".\n\r" % (instance.position, instance.field_set.pk,
                   instance.form_template.pk)

        logger.info(msg)

    else:

        orig_field = FieldTemplate.objects.get(pk=instance.pk)

        if instance.field_set == orig_field.field_set:

            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set).exclude(pk=instance.pk)

            position_list = [f.position for f in fields]

            if instance.position in position_list:

                FieldTemplate.objects.filter(
                    position=instance.position).update(position=orig_field.position)

        else:

            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template, field_set=instance.field_set)

            instance.position = fields.count() + 1

            old_field_set_fields = FieldTemplate.objects.filter(
                form_template=orig_field.form_template,
                field_set=orig_field.field_set, position__gt=orig_field.position
            )

            for field in old_field_set_fields:
                FieldTemplate.objects.filter(pk=field.pk).update(position=field.position-1)


        if instance.field_set is None:
            fs = None
        else:
            fs = instance.field_set.pk

        msg = "FieldTemplate [id:%s] set to "\
        "position [%s], field_set [id:%s], form_template [id:%s]"\
        ".\n\r" % (instance.pk, instance.position,
                  fs, instance.form_template.pk)

        logger.info(msg)


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

        msg = "FieldTemplate [id:%s] deleted. Updating Field Template [id:%s]"\
        "position [%s], field_set [id:%s], form_template [id:%s]"\
        ".\n\r" % (instance.pk, field.pk, field.position,
                  field.field_set.pk, field.form_template.pk)

        logger.info(msg)
