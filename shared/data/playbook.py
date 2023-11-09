from shared import Component
from os.path import abspath, join, exists
from yaml import safe_load


class Playbook:
    PUBLIC_METADATA_FIELDS = [('component_name', 'Unnamed component'), ('family', 'general'), ('maintainers', []),
                              ('version', '0.0'), ('depends', []), ('short_description', 'No description'),
                              ('long_description', 'No description'), ('platforms', []), ('sites', [])]

    class ComponentFlows:
        class Step:
            def __init__(self, data: {}, baseFolder: str):
                self.Tool = data['tool']
                self.FileRelative = data['file']
                self.File = data['file'].replace('./', '')
                self.File = join(baseFolder, *self.File.split('/'))

            def __str__(self):
                return f"Step <{self.Tool}: '{self.File}'>"

            @property
            def Serialized(self):
                return {'tool': self.Tool, 'file': self.File}

            @property
            def RedactedSerialized(self):
                return {'tool': self.Tool, 'file': self.FileRelative}

        def __init__(self, data: {}, baseFolder: str):
            self.data = {}
            for name, steps in [e for e in data.get('flow', {}).items()]:
                name = name.lower()
                self.data[name] = []
                for step in steps:
                    self.data[name].append(Playbook.ComponentFlows.Step(step, baseFolder))

        def __getitem__(self, item: str) -> [Step]:
            return self.data.get(item.lower(), [])

        @property
        def Available(self):
            return self.data.keys()

        @property
        def Serialized(self):
            res = {}
            for flow, steps in self.data.items():
                res[flow] = [s.RedactedSerialized for s in steps]
            return res

    class ComponentMetadataType:
        def __init__(self, data: {}):
            self.data = {}
            for field in Playbook.PUBLIC_METADATA_FIELDS:
                name, default = field
                self.data[name] = data.get(name, default)

        @property
        def Serialized(self):
            return self.data

    class SnapshotMetadataType:
        def __init__(self, data: {}):
            self.Address = data.get('Address', None)
            self.Commit = data.get('Commit', None)
            self.Message = data.get('Message', None)
            self.Date = data.get('Date', None)

        @property
        def Serialized(self):
            return {'address': self.Address, 'commit': self.Commit,
                    'message': self.Message, 'date': self.Date}

    def __init__(self, component: Component, parent: 'TrialNetwork'):
        self.folder = join(parent.Folder, 'Playbooks', component.Name)
        if self.SnapshotMetadata is None:  # There is no frozen copy of the component's playbook
            component.CopyToLocalFolder(self.folder)

        self.snapshotMetadata: Playbook.SnapshotMetadata | None = None
        self.componentMetadata: Playbook.ComponentMetadata | None = None
        self.publicValues: {} = None
        self.flows: Playbook.ComponentFlows | None = None

    @property
    def SnapshotMetadata(self) -> SnapshotMetadataType | None:
        path = join(self.folder, 'metadata.yml')
        if exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    return Playbook.SnapshotMetadataType(safe_load(file))
            except Exception as e:
                raise RuntimeError(f"Unable to load playbook metadata from '{path}'") from e
        else:
            return None

    def loadFromPublicDescription(self):
        path = join(self.folder, 'public', 'description.yml')
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data: {} = safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Unable to read playbook description '{path}': {e}") from e

        self.componentMetadata = Playbook.ComponentMetadataType(data)
        for field in self.PUBLIC_METADATA_FIELDS:
            _ = data.pop(field[0])  # Remove all known metadata fields, the rest are variables

        self.publicValues = data

    @property
    def ComponentMetadata(self) -> ComponentMetadataType:
        if self.componentMetadata is None:
            self.loadFromPublicDescription()
        return self.componentMetadata

    @property
    def PublicValues(self) -> {}:
        if self.publicValues is None:
            self.loadFromPublicDescription()
        return self.publicValues

    @property
    def Flow(self) -> ComponentFlows:
        if self.flows is None:
            path = join(self.folder, 'private', 'manifest.yaml')
            with open(path, 'r', encoding='utf-8') as file:
                data = safe_load(file)
                self.flows = Playbook.ComponentFlows(data, self.folder)
        return self.flows

    @property
    def Serialized(self):
        return {
            'metadata': self.ComponentMetadata.Serialized,
            'snapshot': self.SnapshotMetadata.Serialized,
            'flows': self.Flow.Serialized,
            'values': self.PublicValues
        }
