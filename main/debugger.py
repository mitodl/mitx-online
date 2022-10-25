import os


def init_debugpy():
    from django.conf import settings

    port = int(os.environ.get("DEBUGPY_PORT"))

    if settings.DEBUG and port:
        import debugpy

        debugpy.log_to('logs/')
        debugpy.configure(python="python")
        debugpy.listen(("0.0.0.0", port))
        print(f"Debugpy is listening on 0.0.0.0:{port}")
