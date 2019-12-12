from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import ugettext_lazy as _

from M4.System.models.models import Asset, Datapoint, Sla, CustomField, Frontend, Setting, TriggerPlugin
from flexselect import FlexSelectWidget


class CustomFieldInline(GenericTabularInline):
    model = CustomField
    extra = 1
    ct_field_name = 'content_type'
    id_field_name = 'object_id'


class TriggerTypeWidget(FlexSelectWidget):
    """
    The widget must extend FlexSelectWidget and implement trigger_fields,
    details(), queryset() and empty_choices_text().
    """

    trigger_fields = ['datatype']
    """Fields which on change will update the base field."""

    def details(self, base_field_instance, instance):
        if base_field_instance is None:
            return ''
        """
        HTML appended to the base_field.

        - base_field_instance: An instance of the base_field.
        - instance: A partial instance of the parent model loaded from the
                    request.

        Returns a unicoded string.
        """
        return u"""\
        <div>
            <dl>
                <dt>%s</dt><dd>%s</dd>
                <dt>%s</dt><dd>%s</dd>
                <dt>%s</dt><dd>%s</dd>
            </dl>
        </div>
        """ % (_('Name'), base_field_instance.content_object.title,
               'Type', base_field_instance.content_object.datatype,
               _('Plugin'), base_field_instance.content_type.app_label,
               )

    def queryset(self, instance):
        """
        Returns the QuerySet populating the base field. If either of the
        trigger_fields is None, this function will not be called.

        - instance: A partial instance of the parent model loaded from the
                    request.
        """
        if instance:
            return TriggerPlugin.objects.filter(datatype=instance.datatype)
        return TriggerPlugin.objects.all()

    def empty_choices_text(self, instance):
        """
        If either of the trigger_fields is None this function will be called
        to get the text for the empty choice in the select box of the base
        field.

        - instance: A partial instance of the parent model loaded from the
                    request.
        """
        return "Please update the datatype field"


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    inlines = (CustomFieldInline,)


@admin.register(Datapoint)
class DatapointAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Alters the widget displayed for the base field.
        """
        if db_field.name == "trigger":
            kwargs['widget'] = TriggerTypeWidget(
                base_field=db_field,
                modeladmin=self,
                request=request,
            )
            kwargs['label'] = _('Trigger')
        return super(DatapointAdmin, self).formfield_for_foreignkey(db_field,
                                                                    request, **kwargs)

    inlines = (CustomFieldInline,)


@admin.register(Sla)
class SlaAdmin(admin.ModelAdmin):
    inlines = (CustomFieldInline,)


@admin.register(Frontend)
class FrontendAdmin(admin.ModelAdmin):
    pass


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    pass
