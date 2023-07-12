import functools
import time

from memory_profiler import memory_usage


def benchmark_decorator(file_name):
    def actual_decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_mem = memory_usage()[0]
            start_time = time.time()

            result = await func(*args, **kwargs)

            end_time = time.time()
            end_mem = memory_usage()[0]

            elapsed_time = end_time - start_time
            mem_diff = end_mem - start_mem

            with open(file_name, 'a') as f:
                f.write(f"{args[1]['model_name']};{elapsed_time};{mem_diff}\n")

            return result

        return async_wrapper

    return actual_decorator
