import sentry_sdk

from settings import settings

sentry_sdk.init(
    settings.SENTRY_URL,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


try:
    division_by_zero = 1 / 0
except:
    pass
var1 = 1

class A:
    x=1
    pass

var_a = A()
raise TypeError('manual error')