from M4.System.signals import post_fetch
from django.dispatch import receiver
from M4.System.tools import error, dbg, die


@receiver(post_fetch)
def check_trigger(sender, **kwargs):

    dbg('retval Message: ')
    dbg(**kwargs)
    print("Fetch finished,we need to check the value against the threshold!")