import os

from configuration.Config import CULL_DIR

class PSRestKillQueue(object):
    def kill(self, pid: str) -> None:
        open(f'{CULL_DIR}/{pid}', 'w').close()

    def get(self, *pids: str) -> list:
        files = [pid for pid in pids if os.path.isfile(f'{CULL_DIR}/{pid}')]

        for file in files:
            os.remove(file)

        return files