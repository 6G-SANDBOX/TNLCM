from threading import Lock
from os.path import join, abspath, exists
from os import makedirs
from dulwich import porcelain
from yaml import safe_load


class Repository:
    baseFolder = abspath('./REPOSITORIES')

    def __init__(self, address: str, user: str, password: str):
        self.lock = Lock()
        self.address = address
        self.user = user
        self.password = password

        folder = address
        folder = folder.replace('https://', '').replace('http://', '')
        self.localPath = join(self.baseFolder, *folder.split('/'))

        self.UpdateLocalRepository()

    def UpdateLocalRepository(self):
        with self.lock:
            if not exists(join(self.localPath, '.git', 'HEAD')):
                makedirs(self.localPath, exist_ok=True)
                porcelain.clone(self.address, target=self.localPath, username=self.user, password=self.password)
            else:
                porcelain.fetch(self.localPath)


class Library:
    repositories: {str, Repository} = {}

    @classmethod
    def Initialize(cls):
        with open('../repositories.yml', 'r', encoding='utf-8') as file:
            data = safe_load(file)

        for name, definition in data['Repositories'].items():
            repository = Repository(definition['Address'],
                                    definition.get('User', None),
                                    definition.get('Password', None))
            cls.repositories[name] = repository

