class UnsupportedService(Exception):
    """Raised when the service is not supported"""
    pass


class UnsupportedServiceMetric(Exception):
    """Raised when the service does not support the given metric"""
    pass


class MetricMakerError(Exception):
    """Raised when the metric maker fails"""
    pass
