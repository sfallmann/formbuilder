from django.conf import settings
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.db.models.signals import post_delete, pre_delete
from .models import FormTemplate, FieldTemplate, FieldSet

import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=FormTemplate)
def create_none_field_set(sender, instance, created, **kwargs):

    if created:

        FieldSet.objects.create(
            form_template=instance,
            name=settings.EMPTY_FIELDSET,
            label=""
        )


@receiver(post_delete, sender=FieldTemplate)
def adjust_fieldtemplate_positions(sender, instance, **kwargs):

    """
    On a FieldTemplate instance delete, updates the position
    of all related FieldTemplate instances.
    """

    #  Get all the fields in the FormTemplate and FieldSet that the deleted
    #  FieldTemplate was in.
    try:
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
                ".\n\r" % (
                    instance.pk, field.pk, field.position,
                    field.field_set.pk, field.form_template.pk
                )

            logger.info(msg)

    except ObjectDoesNotExist as e:
        print e
        #logger.info(msg)


@receiver(post_delete, sender=FieldSet)
def adjust_fieldset_position(sender, instance, **kwargs):

    all_fieldsets = FieldSet.objects.filter(
        form_template=instance.form_template,
        position__gt=instance.position
    ).order_by('position')

    #  Decrement the position of the FieldSets
    for fieldset in all_fieldsets:

        FieldSet.objects.filter(
            pk=fieldset.pk).update(position=fieldset.position-1)


@receiver(post_delete, sender=FieldSet)
def delete_fieldset_cleanup(sender, instance, **kwargs):

    if FieldSet.objects.filter(
        form_template=instance.form_template,
        name=settings.EMPTY_FIELDSET
    ):
        fs = FieldSet.objects.get(
                form_template=instance.form_template,
                name=settings.EMPTY_FIELDSET
            )

        fields = FieldTemplate.objects.filter(
            form_template=instance.form_template, field_set=fs)

        for f in fields:
            f.field_set = fs


@receiver(pre_save, sender=FieldSet)
def intialize_fieldset_values(sender, instance, **kwargs):

    """
    Sets a FieldSets instance's position on an save.  Change's all other
    related FieldSet instances positions accordingly.
    """

    #  Check if the save was for a newly created FieldTemplate instance
    if instance.pk is None:

        #  Get a queryset of all the FieldSetss with the same
        #  form_template

        fieldsets = FieldSet.objects.filter(
            form_template=instance.form_template)

        #  Set the new instances position to fields.count + 1
        instance.position = fieldsets.count() + 1


    #  For an existing FieldSet instance
    else:

        orig_fieldset = FieldSet.objects.get(pk=instance.pk)
        #  Get all the FieldTemplate instances with the instances field_set
        #  but exclude the instance from the query
        fieldsets = FieldSet.objects.filter(
            form_template=instance.form_template).exclude(pk=instance.pk)

        #  Make list of positions from fields
        position_list = [f.position for f in fieldsets]

        #  If the instance's position is in the list, it was changed
        #  to another instance's position.
        #  This will give the other instance, the old position in effect
        #  swapping positions.
        if instance.position in position_list:

            FieldSet.objects.filter(
                position=instance.position).update(
                position=orig_fieldset.position)


@receiver(pre_save, sender=FieldTemplate)
def intialize_fieldtemplate_values(sender, instance, **kwargs):

    """
    Sets a FieldTemplates instance's position on an save.  Change's all other
    related FieldTemplate instances positions accordingly.
    """

    fs = FieldSet.objects.get(
            form_template=instance.form_template,
            name=settings.EMPTY_FIELDSET
        )

    if instance.field_set is None:
        instance.field_set = fs

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

        if not instance.label:
            instance.label = instance.name.title()

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

        msg = "FieldTemplate [id:%s] set to "\
            "position [%s], field_set [id:%s], form_template [id:%s]"\
            ".\n\r" % (
                instance.pk, instance.position,
                instance.field_set.pk, instance.form_template.pk
            )

        logger.info(msg)



