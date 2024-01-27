import asyncio

from pygtest import dependency
from dependency import Dependency


class A(Dependency):
    pass


class Conflicts_with_A(Dependency):
    def have_conflict(self, other_dep):
        if isinstance(other_dep, A):
            return True


@dependency(A())
async def test_one():
    await asyncio.sleep(5)


@dependency(Conflicts_with_A())
async def test_two():
    await asyncio.sleep(5)


@dependency(Conflicts_with_A())
async def test_three():
    await asyncio.sleep(5)


async def test_without_deps():
    await asyncio.sleep(5)
