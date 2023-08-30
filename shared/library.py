from yaml import safe_load
from dulwich import porcelain
from typing import Optional, Dict
from os.path import join, exists
from os import makedirs


class Playbook:
    def __init__(self, folder: str):
        self.folder = folder
        self.public_values = None
        self.private_manifest = None

    @property
    def Commit(self):
        return porcelain.describe(self.folder)

    @property
    def PublicValues(self):
        if self.public_values is None:
            path = join(self.folder, 'skel', 'public', 'values.yaml')
            with open(path, 'r', encoding='utf-8') as file:
                self.public_values = safe_load(file)
        return self.public_values

    @property
    def Flow(self) -> [str]:
        if self.private_manifest is None:
            path = join(self.folder, 'skel', 'private', 'manifest.yaml')
            with open(path, 'r', encoding='utf-8') as file:
                self.private_manifest = safe_load(file)
        return self.private_manifest['flow']


class Library:
    baseFolder = "../Playbooks"

    initialized = False
    sources: Optional[Dict[str, str]] = None
    playbooks: Dict[str, Optional[Playbook]] = {}
    user = password = None

    @classmethod
    def Init(cls):
        with open("../playbooks.yml", 'r', encoding='utf-8') as file:
            cls.sources = safe_load(file)
            cls.user = cls.sources['Credentials']['User']  # TODO: Improve
            cls.password = cls.sources['Credentials']['Pass']


    @classmethod
    def GetPlaybook(cls, name: str):
        if not cls.initialized: cls.Init()

        res = cls.playbooks.get(name, None)

        if res is None:
            repository = cls.sources.get(name, None)
            if repository is not None:
                folder = repository
                folder = folder.replace('https://', '').replace('http://', '')
                folder = join(cls.baseFolder, *folder.split('/'))

                if not exists(join(folder, '.git', 'HEAD')):
                    makedirs(folder, exist_ok=True)
                    porcelain.clone(repository, target=folder, username=cls.user, password=cls.password)

                res = Playbook(folder)
                cls.playbooks[name] = res
                return res
            else:
                return None  # Unknown entity type
        else:
            return res  # Already cached
