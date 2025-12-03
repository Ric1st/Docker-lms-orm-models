# /code/core/throttling.py
from ninja.throttling import AnonRateThrottle, AuthRateThrottle


class SimpleRateThrottle(AnonRateThrottle):
    """
    Simple rate throttling untuk anonymous users
    Membatasi 10 request per detik
    """
    def __init__(self):
        super().__init__('10/s')


class NoReadsThrottle(AnonRateThrottle):
    """
    Custom throttle yang tidak membatasi GET requests
    Hanya membatasi POST, PUT, DELETE, PATCH
    """
    def __init__(self):
        super().__init__('100/m')
    
    def allow_request(self, request):
        """Do not throttle GET requests"""
        if request.method == "GET":
            return True
        return super().allow_request(request)


class StrictPostThrottle(AuthRateThrottle):
    """
    Throttle ketat untuk POST requests
    Membatasi 50 POST requests per menit untuk authenticated users
    """
    def __init__(self):
        super().__init__('50/m')
    
    def allow_request(self, request):
        """Only throttle POST requests"""
        if request.method != "POST":
            return True
        return super().allow_request(request)


class DailyLimitThrottle(AuthRateThrottle):
    """
    Throttle berdasarkan limit harian
    Membatasi 10000 requests per hari untuk authenticated users
    """
    def __init__(self):
        super().__init__('10000/d')