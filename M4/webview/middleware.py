def process_request(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        pass
    else:
        # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
        # Take just the first one.
        real_ip = real_ip.split(",")[0]
        request.META['REMOTE_ADDR'] = real_ip


class SetRemoteAddrFromForwardedFor(object):
    # Add support for reverse proxying django
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
