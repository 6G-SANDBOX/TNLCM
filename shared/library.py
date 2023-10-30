from threading import Lock
from os.path import join, abspath, exists
from os import makedirs
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.client import HttpGitClient
from dulwich.objects import Commit
from yaml import safe_load, safe_dump
from shared import Log, Level
from shared import Cli, IO


class Repository:
    def __init__(self, baseFolder: str, address: str, user: str, password: str, maybeDefaultBranch: str | None):
        self.lock = Lock()
        self.lastCliCommand = []

        self.user = user
        self.password = password

        self.Address = address
        self.DefaultBranch = maybeDefaultBranch  # Assume we know the default branch, should be overriden later if not

        folder = address
        folder = folder.replace('https://', '').replace('http://', '')
        self.LocalPath = join(baseFolder, *folder.split('/'))

        self.remoteRepo = HttpGitClient(self.Address, self.user, self.password)  # Unused, for checkouts with porcelain
        self.localRepo = None
        self.UpdateLocalRepository()

    def _recordLastCliCommand(self, level: Level | str, msg: str, logger: str | None = None):
        self.lastCliCommand.append(msg)

    def checkout(self, target: str):
        # TODO: It's a bit silly to use a library for handling git, then having to fall back to the CLI for /this/.
        #  https://stackoverflow.com/a/69909226 describes a correct way of doing checkouts with porcelain, but
        #  fails for branches that are rooted before the default branch.
        # TODO: This won't work for private repositories.

        self.lastCliCommand = []
        cli = Cli(['git', 'checkout', target], self.LocalPath, self._recordLastCliCommand)

        Log.I(f'Running {cli} ...')
        code = cli.Execute()
        level = Level.DEBUG if code == 0 else Level.ERROR
        Log.Log(level, f'Command finished with return code: {code}')
        for line in self.lastCliCommand:
            Log.D(line)

    def UpdateLocalRepository(self):
        with self.lock:
            if not exists(join(self.LocalPath, '.git', 'HEAD')):
                makedirs(self.LocalPath, exist_ok=True)
                self.localRepo = porcelain.clone(self.Address, target=self.LocalPath,
                                                 username=self.user, password=self.password)
                self.DefaultBranch = porcelain.active_branch(self.LocalPath).decode(encoding='utf8')
            else:
                self.localRepo = Repo(self.LocalPath)

            porcelain.fetch(self.localRepo)

    def CopyComponentToLocalFolder(self, target: str, componentFolder: str, branch: str, commit: str) -> str:
        """
        Makes a copy of a single component in a repository, in the specified folder. Then includes an extra
        'metadata.yml' file with information about the repository 'Address', 'Commit' and 'Message' of the commit
        :returns The folder where the component has been saved, as str
        """

        with self.lock:
            head = commit if commit is not None else \
                (branch if branch is not None else self.DefaultBranch)

            self.checkout(head)

            target = abspath(target)
            IO.EnsureFolder(target)

            source = join(self.LocalPath, componentFolder)
            IO.CopyFolderContents(source, target)

            commit: Commit = self.localRepo[b'HEAD']
            metadata = {
                'Address': self.Address,
                'Commit': commit.id.decode(),
                'Message': commit.message.decode()
            }
            with open(join(target, 'metadata.yml'), 'w', encoding='utf-8') as file:
                safe_dump(metadata, file)

            return target


class Component:
    def __init__(self, name: str, data: {}):
        self.Name = name
        self.Repository = data['Repository']
        self.Folder = data['Folder']
        self.Branch = data.get('Branch', None)
        self.Commit = data.get('Commit', None)

    def CopyToLocalFolder(self, target: str, branch: str = None, commit: str = None) -> str:
        """:returns The folder where the component has been stored (<target>/<component folder in library>)"""

        branch = branch if branch is not None else self.Branch
        commit = commit if commit is not None else self.Commit

        repository = Library.GetRepository(self.Repository)
        if repository is not None:
            return repository.CopyComponentToLocalFolder(target, self.Folder, branch, commit)
        else:
            raise RuntimeError(f"Repository for component '{self.Name}' not found ('{self.Repository}')")


class Library:
    baseFolder: str = ''
    defaultBranch: {str, str} = {}
    repositories: {str, Repository} = {}
    components: {str, Component} = {}

    @classmethod
    def Initialize(cls):
        from shared.settings import CoreSettings, ComponentsSettings, RepositoriesSettings

        settings = CoreSettings()
        cls.baseFolder = abspath(settings.Folders.Repositories)

        IO.EnsureFolder(cls.baseFolder)

        upkeepPath = join(cls.baseFolder, 'upkeep.yml')
        if exists(upkeepPath):
            with open(upkeepPath, 'r', encoding='utf-8') as file:
                data = safe_load(file)
                cls.defaultBranch = data.get('DefaultBranches', {})

        repositories = RepositoriesSettings().Repositories
        for name, definition in repositories.items():
            repository = Repository(cls.baseFolder,
                                    definition['Address'],
                                    definition.get('User', None),
                                    definition.get('Password', None),
                                    cls.defaultBranch.get(name, None))
            cls.repositories[name] = repository
            cls.defaultBranch[name] = repository.DefaultBranch

        components = ComponentsSettings().Components
        for name, definition in components.items():
            cls.components[name] = Component(name, definition)

        with open(upkeepPath, 'w', encoding='utf-8') as file:
            payload = {
                "DefaultBranches": cls.defaultBranch
            }
            safe_dump(payload, file)

    @classmethod
    def GetRepository(cls, name: str) -> Repository | None:
        return cls.repositories.get(name, None)

    @classmethod
    def GetComponent(cls, name: str) -> Component | None:
        return cls.components.get(name, None)

