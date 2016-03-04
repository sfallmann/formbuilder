from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.db.models.signals import post_delete, pre_delete
from .models import FieldTemplate, FieldTemplateOptions
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=FieldTemplate)
def create_options_for_new_fieldtemplate(sender, created, instance, **kwargs):

    """
    Creates a FieldTemplateOptions instance for a FieldTemplate on the
    FieldTemplate's creation.
    """

    #  Check if the save was for a newly created FieldTemplate instance
    if created:

        #  Create a FieldTemplateOption instance for the FieldTemplate
        options = FieldTemplateOptions(field_template=instance)
        options.label = instance.name.title()
        options.save()

        msg = "FieldTemplateOptions [id:%s] created"\
        "for FieldTemplate [id:%s].\n\r" % (instance.pk, options.pk)

        logger.info(msg)

@receiver(pre_save, sender=FieldTemplate)
def set_field_template_position_save(sender, instance, **kwargs):

    """
    Sets a FieldTemplates instance's position on an save.  Change's all other
    related FieldTemplate instances positions accordingly.
    """

    #  Check if the save was for a newly created FieldTemplate instance
    if instance.pk is None:

        #  Get a queryset of all the FieldTemplates with the same
        #  form_template and field_set=None
        #
        #  All new FieldTemplate instances have field_set=None


        fields = FieldTemplate.objects.filter(
            form_template=instance.form_template, field_set=instance.field_set)


        #  Set the new instances position to fields.count + 1
        instance.position = fields.count() + 1

        msg = "New FieldTemplate. Set to "\
        "position [%s], field_set NONE, form_template [id:%s]"\
        ".\n\r" % (instance.position, instance.form_template.pk)

        logger.info(msg)
    #  For an existing FieldTemplate instance
    else:

        #  Get the values for the instance in the database
        #  This is so the original field_set and position can be tracked
        orig_field = FieldTemplate.objects.get(pk=instance.pk)

        #  Check if the field_set remained the same
        if instance.field_set == orig_field.field_set:

            #  Get all the FieldTemplate instances with the instances field_set
            #  but exclude the instance from the query
            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set).exclude(pk=instance.pk)

            #  Make list of positions from fields
            position_list = [f.position for f in fields]

            #  If the instance's position is in the list, it was changed
            #  to another instance's position.
            #  This will give the other instance, the old position in effect
            #  swapping positions.
            if instance.position in position_list:

                FieldTemplate.objects.filter(
                    position=instance.position).update(
                    position=orig_field.position)

        #  If the instance was assigned a different FieldSet
        else:

            # Get all the FieldTemplate instance with the same FormTemplate and
            # FieldSet as this one
            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set
            )

            #  Give position the count of all FieldTemplates already in the
            #  FieldSet.
            instance.position = fields.count() + 1

            #  Get all the FieldTemplates in the old FieldSet (or None) that
            #  has a position greater than the instance had
            old_field_set_fields = FieldTemplate.objects.filter(
                form_template=orig_field.form_template,
                field_set=orig_field.field_set,
                position__gt=orig_field.position
            )
            #  Since the instance is no longer in the FieldSet decrement all
            #  the positions
            for field in old_field_set_fields:
                FieldTemplate.objects.filter(
                    pk=field.pk).update(
                    position=field.position-1
                )

        #  Set fs to None to avoid throwing an error
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

    """
    On a FieldTemplate instance delete, updates the position
    of all related FieldTemplate instances.
    """

    #  Get all the fields in the FormTemplate and FieldSet that the deleted
    #  FieldTemplate was in.
    all_fields = FieldTemplate.objects.filter(
        form_template=instance.form_template,
        field_set=instance.field_set,
        position__gt=instance.position
    ).order_by('position')

    #  Decrement the position of the FieldTemplates
    for field in all_fields:
        FieldTemplate.objects.filter(
            pk=field.pk).update(position=field.position-1)

        msg = "FieldTemplate [id:%s] deleted. Updating Field Template [id:%s]"\
        "position [%s], field_set [id:%s], form_template [id:%s]"\
        ".\n\r" % (instance.pk, field.pk, field.position,
                  field.field_set.pk, field.form_template.pk)

        logger.info(msg)
