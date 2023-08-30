from yaml import safe_load
from dulwich import porcelain
from typing import Optional, Dict
from os.path import join, exists
from os import makedirs


class Library:
    playbooks: Optional[Dict[str, str]] = None
    baseFolder = "../Playbooks"
    user = password = None

    @classmethod
    def GetPlaybook(cls, name: str):
        if cls.playbooks is None:
            with open("../playbooks.yml", 'r', encoding='utf-8') as file:
                cls.playbooks = safe_load(file)
                cls.user = cls.playbooks['Credentials']['User']
                cls.password = cls.playbooks['Credentials']['Pass']

        repository = cls.playbooks.get(name, None)
        if repository is not None:
            folder = repository
            folder = folder.replace('https://', '').replace('http://', '')
            folder = join(cls.baseFolder, *folder.split('/'))
            print(f"{repository} - {folder}")
            if not exists(join(folder, '.git', 'HEAD')):
                makedirs(folder, exist_ok=True)
                porcelain.clone(repository, target=folder, username=cls.user, password=cls.password)

            return folder
        else:
            return None




