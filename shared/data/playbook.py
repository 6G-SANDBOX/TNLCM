from shared import Component
from os.path import abspath, join, exists
from yaml import safe_load


class Playbook:
    class PlaybookMetadata:
        def __init__(self, data: {}):
            self.Address = data.get('Address', None)
            self.Commit = data.get('Commit', None)
            self.Message = data.get('Message', None)

    def __init__(self, component: Component, parent: 'TrialNetwork'):
        self.folder = join(parent.Folder, 'Playbooks', component.Name)
        if self.Metadata is None:  # There is no frozen copy of the component's playbook
            component.CopyToLocalFolder(self.folder)

        self.public_values = None
        self.private_manifest = None

    @property
    def Metadata(self) -> PlaybookMetadata | None:
        path = join(self.folder, 'metadata.yml')
        if exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    return Playbook.PlaybookMetadata(safe_load(file))
            except Exception as e:
                raise RuntimeError(f"Unable to load playbook metadata from '{path}'") from e
        else:
            return None

    @property
    def PublicValues(self):
        # if self.public_values is None:
        #     path = join(self.folder, 'skel', 'public', 'values.yaml')
        #     with open(path, 'r', encoding='utf-8') as file:
        #         self.public_values = safe_load(file)
        # return self.public_values
        return {}  # TODO: Update with new format

    @property
    def Flow(self) -> [str]:
        # if self.private_manifest is None:
        #     path = join(self.folder, 'skel', 'private', 'manifest.yaml')
        #     with open(path, 'r', encoding='utf-8') as file:
        #         self.private_manifest = safe_load(file)
        # return self.private_manifest['flow']
        return []  # TODO: Update with new format
