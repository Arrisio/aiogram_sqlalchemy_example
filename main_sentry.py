import sentry_sdk
sentry_sdk.init(
    "https://ddd4989f99784a1d9e5d44b8f2e39395@o1081734.ingest.sentry.io/6089540",

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