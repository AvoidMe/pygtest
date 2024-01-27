import asyncio


class Dependency:
    def __init__(self):
        self.reset()

    def reset(self):
        self.instances = 0
        self.resolved = asyncio.Event()

    def _setup(self):
        self.instances += 1

    async def _teardown(self):
        self.instances -= 1
        if self.instances == 0:
            await self.teardown()
            self.resolved.set()

    # Intended to be overwritten by child deps
    def have_conflict(self, other_dep):
        return False

    # Intended to be overwritten by child deps
    async def setup(self):
        pass

    # Intended to be overwritten by child deps
    async def teardown(self):
        pass
