from django.conf import settings
from django.core.signals import setting_changed
from rest_framework.settings import APISettings


class Settings(APISettings):

    SETTINGS_KEY = 'CELERY_PANTRY'

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, self.SETTINGS_KEY, {})
        return self._user_settings


DEFAULTS = {
    'CUSTOM_HANDLER': None
}
IMPORT_STRINGS = (
    'CUSTOM_HANDLER',
)
pantry_settings = Settings(None, DEFAULTS, IMPORT_STRINGS)


def reload_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == Settings.SETTINGS_KEY:
        pantry_settings.reload()


setting_changed.connect(reload_settings)
