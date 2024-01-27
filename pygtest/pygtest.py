import asyncio
import contextlib
import sys

from pytest import Session as PytestSession
from _pytest.config import _prepareconfig, ExitCode

from pygtest.runner import TestsRunner


@contextlib.contextmanager
def pytest_wrapper():
    config = _prepareconfig()
    config._do_configure()
    session = PytestSession.from_config(config)
    config.hook.pytest_sessionstart(session=session)
    yield config, session
    config.hook.pytest_sessionfinish(session=session, exitstatus=ExitCode.OK)


async def pygtest_main():
    runner = TestsRunner()
    with pytest_wrapper() as (config, session):
        tests = [
            runner.test_wrapper(test)
            for test in session.perform_collect(sys.argv[1:])
        ]
        tasks = [test() for test in tests]
        await asyncio.gather(*tasks)


def dependency(dep):
    def _wrapper(func):
        if getattr(func, "_deps", None) is None:
            func._deps = []
        if isinstance(dep, (list, tuple)):
            func._deps.extend(dep)
        else:
            func._deps.append(dep)
        return func
    return _wrapper
