==================================
Testing Feature Flags from Posthog
==================================

This document is intended to offer information regarding testing PostHog feature flags either manually, as during a pull request review, or automatically, as during a test run.

************
Django Flags
************

Django flags will still send to posthog, regardless of environment.  You can visit `this insight <https://us.posthog.com/project/33038/insights/mYJ7ngbN>`_ in posthog to see the feature flag use and see that your request is being received and logged as expected.

In order to see the request in real time, posthog offers some `example code <https://github.com/PostHog/posthog-python/blob/master/example.py>`_.  Another approach would be to check the return value of the `main.features.is_enabled` function. This can be helpful both when testing manually to ensure the feature flag is returning the value expected.

To change a feature flag, you can modify the value for that feature flag when `environment=dev` to whatever value is needed.  This should be done in the PostHog dashboard.  You can also toggle debug mode on and off by setting `posthog.debug`.

PostHog is set to disabled mode when running tests.


**************
Frontend Flags
**************

Frontend flags are not sent to PostHog from your local setup.  You can turn this off by removing the conditional

.. code-block:: javascript

    if (environment === "dev") {
        posthog.debug()
    }

from `frontend/public/src/lib/util.js`.

In order to override the value, you can set `posthog.featureFlags.override()` to the value you want to test.  This can be done in the console of your browser or in code.
