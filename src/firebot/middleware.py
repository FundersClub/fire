def XForwardedForMiddleware(get_response):
    def middleware(request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        return get_response(request)
    return middleware
