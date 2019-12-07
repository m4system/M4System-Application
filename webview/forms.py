from django import forms

# Basic form for the user profile settings
class SettingsForm(forms.Form):
    notifemail = forms.EmailField(label='Notification Email', required=False, help_text='Fill this field to receive email alerts')
    notifcallback = forms.URLField(label='Notification URL', max_length=100, required=False, help_text='Fill this field to receive POST callbacks to the specified URL')
