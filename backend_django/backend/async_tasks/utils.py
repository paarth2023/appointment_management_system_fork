from django.conf import settings

def run_task(task_func, *args, **kwargs):
    """
    Runs task async if broker is enabled,
    otherwise runs synchronously.
    """
    if settings.USE_ASYNC_TASKS:
        task_func.delay(*args, **kwargs)
    else:
        task_func(*args, **kwargs)
