from stevedore import extension


def _load_error_handler(*args, **kwds):
    raise


def load_handlers():
    return extension.ExtensionManager(
        'aeromancer.filehandler',
        invoke_on_load=True,
        on_load_failure_callback=_load_error_handler,
    )
