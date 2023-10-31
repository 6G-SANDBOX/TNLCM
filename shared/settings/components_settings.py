from shared import ConfigBase, Validable, Level


class ComponentsSettings(ConfigBase):
    data = None
    Validation: [(Level, str)] = []

    def __init__(self, forceReload: bool = False):
        super().__init__('components')
        if self.data is None or forceReload:
            self.data = self.Reload()
            self.Validate()

    @property
    def Components(self):
        return self.data.get('Components', {})

    def Validate(self):
        pass  # TODO


