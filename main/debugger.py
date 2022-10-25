import os


def init_debugpy():
    from django.conf import settings

    port = 3000

    if port:
        import debugpy

        debugpy.log_to('logs/')
        debugpy.configure(python="python")
        debugpy.listen(("0.0.0.0", port))
        debugpy.wait_for_client()
        print(f"Debugpy is listening on 0.0.0.0:{port}")
