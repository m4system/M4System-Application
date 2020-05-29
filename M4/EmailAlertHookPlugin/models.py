from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from M4.System.models.base_models import BaseHookPlugin


class EmailTemplate(models.Model):
    name = models.SlugField(verbose_name=_('Email Template Name'), max_length=64, unique=True, blank=True,
                            help_text=_('Internal name, leave empty to autopopulate.'))
    title = models.CharField(verbose_name=_('Email Template Title'), max_length=256,
                             help_text=_('Verbose name for display purposes'))

    def render_template(self):
        return self

    render_template.short_description = _('Render this email template.')

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(EmailTemplate, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Email Templates')
        ordering = ['-name']


class EmailAlertHookPlugin(BaseHookPlugin):
    template_failing = models.ForeignKey(EmailTemplate, related_name='template_failing',
                                         verbose_name=_('Email Template when a fail is trigger.'), help_text=_(
            'Choose or create an email template.  You can use django templating.'), on_delete=models.CASCADE)
    template_recovered = models.ForeignKey(EmailTemplate, related_name='template_recovered',
                                           verbose_name=_('Email Template when recovering.'), help_text=_(
            'Choose or create an email template.  You can use django templating.'), on_delete=models.CASCADE)
    template_error = models.ForeignKey(EmailTemplate, related_name='template_error',
                                       verbose_name=_('Email Template when an error is raised.'), help_text=_(
            'Choose or create an email template.  You can use django templating.'), on_delete=models.CASCADE)
    recipients = models.CharField(verbose_name=_('Recipients List'), max_length=256, blank=True,
                                  help_text=_('Email addresses that will receive the alerts.  Separate with a comma.'))

    def trigger(self):
        return self

    class Meta:
        verbose_name = _('Email Alert')
        verbose_name_plural = _('Email Alerts')
