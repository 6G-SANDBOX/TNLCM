
class EntityDescriptor:
    def __init__(self, name: str, definition: {}, parent: 'TrialNetworkDescriptor'):
        self.Name = name
        self.raw = definition
        self.parent = parent

    @property
    def Type(self) -> str:
        return self.raw.get('Type', str)

    @property
    def Parameters(self) -> {}:
        return self.raw.get('Parameters', {})

    @property
    def Public(self) -> {}:
        return self.raw.get('Public', {})

    @property
    def Depends_on(self) -> {}:
        return self.raw.get('Depends_on', {})

    @property
    def Metadata(self):
        return self.raw.get('Metadata', {})

    @property
    def Serialized(self):
        return {
            'name': self.Name,
            'type': self.Type,
            'parameters': self.Parameters,
            'depends_on': self.Depends_on,
        }

class TrialNetworkDescriptor:
    """
    Description of all the components and configurations. Does not include information about the status of the
    deployed Trial Network (if any).
    """

    def __init__(self, rawDescriptor: {}):
        self.Raw = rawDescriptor
        self.Entities: {str, EntityDescriptor} = {}
        self.Valid = False
        self.ValidationReport: [str] = []
        self.DeploymentOrder: [] = []

        hasErrors = False

        entities = rawDescriptor.get('Infrastructure', {})
        for name, definition in entities.items():
            instance = EntityDescriptor(name, definition, self)
            self.Entities[name] = instance

        order, maybeError = self.calculateDeploymentOrder()

        if maybeError is not None:
            hasErrors = True
            self.ValidationReport.append(maybeError)
        else:
            self.DeploymentOrder = order

        # Additional validations go here

        if not hasErrors:
            self.Valid = True

    def calculateDeploymentOrder(self) -> ([], None):
        res = []
        visited = set()

        def visit(entity_name):
            if entity_name in visited:
                return
            visited.add(entity_name)

            entity = self.Entities[entity_name]
            dependencies = entity.Depends_on.keys()

            for dep_name in dependencies:
                visit(dep_name)

            res.append(entity)

        # Visit each entity to perform topological sorting
        for entity_name in self.Entities.keys():
            visit(entity_name)

        return res, None

    def __str__(self):
        return f'[TND] -> {[f"{e.Name}:{e.Type}"  for e in self.Entities.values()]}'
