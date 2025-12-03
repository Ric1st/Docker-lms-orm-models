# /code/core/throttling.py
from ninja.throttling import AnonRateThrottle, AuthRateThrottle


class SimpleRateThrottle(AnonRateThrottle):
    def __init__(self):
        super().__init__('10/m')


class NoReadsThrottle(AnonRateThrottle):
    def __init__(self):
        super().__init__('10/m')
    
    def allow_request(self, request):
        if request.method == "GET":
            return True
        return super().allow_request(request)


class StrictPostThrottle(AuthRateThrottle):
    def __init__(self):
        super().__init__('10/m')
    
    def allow_request(self, request):
        if request.method != "POST":
            return True
        return super().allow_request(request)


class DailyLimitThrottle(AuthRateThrottle):
    def __init__(self):
        super().__init__('10/m')