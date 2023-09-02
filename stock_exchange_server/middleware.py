import time
from django.core.cache import cache
from django.http import HttpResponse

class RateLimitMiddleware:
    rate = 10  # 10 requests
    per = 60  # per 60 seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/stock/'):
            client_ip = self.get_client_ip(request)
            cache_key = f'rate-limit-{client_ip}'
            requests = cache.get(cache_key, [])

            if len(requests) >= self.rate:
                time_since_first_request = time.time() - requests[0]
                if time_since_first_request <= self.per:
                    return HttpResponse('Too many requests', status=429)
                else:
                    requests = requests[1:]
            
            requests.append(time.time())
            cache.set(cache_key, requests, self.per)

            response = self.get_response(request)
            return response
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
