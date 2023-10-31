from shared import ConfigBase, Validable, Level


class Folders(Validable):
    def __init__(self, data: {}):
        defaults = {
            'Repositories': ('../REPOSITORIES', Level.INFO),
            'TrialNetworks': ('../TRIAL_NETWORKS', Level.INFO)
        }
        super().__init__(data, 'Folders', defaults)

    @property
    def Repositories(self):
        return self._keyOrDefault('Repositories')

    @property
    def TrialNetworks(self):
        return self._keyOrDefault('TrialNetworks')


class CoreSettings(ConfigBase):
    data = None
    Validation: [(Level, str)] = []

    def __init__(self, forceReload: bool = False):
        super().__init__('core')
        if self.data is None or forceReload:
            self.data = self.Reload()
            self.Validate()

    @property
    def Folders(self):
        return Folders(self.data.get('Folders', {}))

    def Validate(self):
        pass  # TODO

