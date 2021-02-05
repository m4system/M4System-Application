from M4.System.signals import post_fetch
from django.dispatch import receiver
from M4.System.tools import error, dbg, die


@receiver(post_fetch)
def check_trigger(sender, retval, datatype, datapoint, **kwargs):

    dbg('retval Message: ')
    error(retval)
    print("Fetch finished,we need to check the value against the threshold!")
