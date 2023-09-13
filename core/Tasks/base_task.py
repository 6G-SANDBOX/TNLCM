from shared.data import TrialNetwork
from re import finditer, match


class BaseTask:
    def __init__(self, tn: TrialNetwork, config: {}):
        self.tn = tn
        self.config: {} = self.expandDict(config, tn.Descriptor["Variables"])
        self.export = self.config.get("Export", {})
        self.internalLog = []

    def Start(self):
        self.Run()
        self.handleExport()

    def Run(self):
        raise NotImplementedError()

    def handleExport(self):
        fullString = ''.join([line.strip() for line in self.internalLog])
        for entry in self.export.items():
            name, regex = entry
            if (m := match(regex, fullString)) is not None:
                value = m[1]
                self.tn.Descriptor["Variables"][name] = value
                print(f"Exported {name} -> {value}")


    @classmethod
    def expandDict(cls, item: object, replacements: {}) -> object:
        if isinstance(item, dict):
            res = {}
            for key, value in item.items():
                res[key] = cls.expandDict(value, replacements)
        elif isinstance(item, list) or isinstance(item, tuple):
            res = []
            for value in item:
                res.append(cls.expandDict(value, replacements))
        elif isinstance(item, str):
            res = cls.expand(item, replacements)
        else:
            res = item
        return res

    @classmethod
    def expand(cls, item: str, replacements: {}) -> str:
        # Expand custom values published by Run.Publish and parameters
        expanded = item
        for match in [m for m in finditer(r'#\{(.*?)}', item)]:
            all = match.group()
            variable = match.groups()[0]

            value = replacements.get(variable, "<<UNKNOWN>>")
            expanded = expanded.replace(all, str(value))

        return expanded
