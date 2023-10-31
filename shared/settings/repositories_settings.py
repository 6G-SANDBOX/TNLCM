from shared import ConfigBase, Validable, Level


class RepositoriesSettings(ConfigBase):
    data = None
    Validation: [(Level, str)] = []

    def __init__(self, forceReload: bool = False):
        super().__init__('repositories')
        if self.data is None or forceReload:
            self.data = self.Reload()
            self.Validate()

    @property
    def Repositories(self):
        return self.data.get('Repositories', {})

    def Validate(self):
        pass  # TODO


