import asyncio
import logging


logger = logging.Logger(__file__)


async def wait_for_deps(dependencies):
    for dep in dependencies:
        await dep.resolved.wait()


class TestsRunner:
    def __init__(self):
        self._deps = []

    def test_wrapper(self, test_func):
        async def wrapper():
            func_deps = getattr(test_func.function, "_deps", [])
            unresolved_deps = func_deps[:]
            # check for conflicts first
            while True:
                tasks = []
                for dep in unresolved_deps:
                    conflicts = []
                    for global_dep in self._deps:
                        if any([
                                global_dep.have_conflict(dep),
                                dep.have_conflict(global_dep),
                        ]):
                            conflicts.append(global_dep)
                    if conflicts:
                        tasks.append(wait_for_deps(conflicts))
                if len(tasks) == 0:
                    break
                await asyncio.gather(*tasks)
            # resolve unresolved deps
            tasks = []
            for dep in func_deps:
                # TODO: check for conflicts with itself
                if dep.instances == 0:
                    tasks.append(dep.setup())
                dep._setup()
                self._deps.append(dep)
            await asyncio.gather(*tasks)
            # run test
            logger.info("Starting test: %s", test_func)
            try:
                await test_func.function()
            except Exception:
                logger.exception("Test is failed")
            else:
                logger.info("Test finished: %s", test_func)
            # tear down deps
            tasks = []
            for dep in func_deps:
                tasks.append(dep._teardown())
            await asyncio.gather(*tasks)
            for dep in func_deps:
                if dep.instances == 0:
                    self._deps.remove(dep)
        return wrapper
