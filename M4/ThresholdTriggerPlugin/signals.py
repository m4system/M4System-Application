from M4.System.signals import post_fetch
from django.dispatch import receiver
import logging


@receiver(post_fetch)
def check_trigger(sender, **kwargs):
    logging.info('retval Message: ' + str(retval))
    print("Fetch finished, we need to check the value against the threshold!" + str(retval))