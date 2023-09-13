
class EntityDescriptor:
    def __init__(self, name: str, definition: {}, parent: 'TrialNetworkDescriptor'):
        self.Name = name
        self.raw = definition
        self.parent = parent

    @property
    def Type(self) -> str:
        return self.raw['Type']

    @property
    def Parameters(self) -> {}:
        return self.raw.get('Parameters', {})

    @property
    def Connections(self) -> {}:
        return self.raw.get('Connections', {})

    @property
    def Monitors(self) -> [str]:
        return self.raw.get('Monitor', [])

    @property
    def DependsOn(self) -> [str]:
        res = set()
        for _, entity in self.Connections.items():
            res.add(entity)
        for entity in self.Monitors:
            res.add(entity.split('.')[0])
        return list(res)

    @property
    def IsRequiredFor(self) -> [str]:
        """Convenience property, this information is handled by the TND"""
        res = self.parent.GetEntityIsRequiredFor(self.Name)
        if res is None:
            raise RuntimeError(f"Inconsistent TND: Entity {self.Name} exists,"
                               f" but TND does not know if it's required for others")
        return res

    @property
    def Serialized(self):
        return {
            'name': self.Name,
            'type': self.Type,
            'parameters': self.Parameters,
            'connections': self.Connections,
            'monitors': self.Monitors,
            'depends_on': self.DependsOn,
            'is_required_for': self.IsRequiredFor
        }

class TrialNetworkDescriptor:
    """
    Description of all the components and configurations. Does not include information about the status of the
    deployed Trial Network (if any).
    """

    def __init__(self, rawDescriptor: {}):
        self.Raw = rawDescriptor
        self.Entities: {str, EntityDescriptor} = {}
        self.requiredFor: {str, [str]} = {}
        self.Valid = False
        self.ValidationReport: [str] = []
        self.DeploymentOrder: [str] = []

        hasErrors = False

        entities = rawDescriptor.get('Infrastructure', {})
        for name, definition in entities.items():
            instance = EntityDescriptor(name, definition, self)
            self.Entities[name] = instance
            self.requiredFor[name] = []  # First create all entities and fill the dict

        # Then traverse entities and fill the lists
        for name, entity in self.Entities.items():
            for depends in entity.DependsOn:
                try:
                    self.requiredFor[depends].append(name)
                except KeyError:
                    hasErrors = True
                    self.ValidationReport.append(f"Entity '{entity.Name}' depends on '{depends}', which does not exist.")

        order, maybeError = self.calculateDeploymentOrder()

        if maybeError is not None:
            hasErrors = True
            self.ValidationReport.append(maybeError)
        else:
            self.DeploymentOrder = order

        # Additional validations go here

        if not hasErrors:
            self.Valid = True

    def calculateDeploymentOrder(self) -> ([], str | None):
        def _checkDependencies(item: str) -> (str, None):
            for dependency in self.Entities[item].DependsOn:
                if dependency not in order:
                    _ = sortedbydependent.remove(dependency)
                    order.insert(0, dependency)
                    return _checkDependencies(dependency)
                else:
                    itemPosition = order.index(item)
                    dependencyPosition = order.index(dependency)
                    if itemPosition > dependencyPosition:
                        pass  # We have a dependency, but will be deployed before this element
                    else:
                        return f"Detected a dependency cycle that includes elements '{item}' and '{dependency}'"
            return None  # No issues detected

        # Build dependency graph
        sortedbydependent = sorted(self.requiredFor.keys(), key=lambda e: len(self.requiredFor[e]), reverse=True)
        order = []

        while len(sortedbydependent) > 0:
            item = sortedbydependent.pop(0)
            order.append(item)
            maybeError = _checkDependencies(item)
            if maybeError is not None:
                return [], maybeError

        return order, None

    def GetEntityIsRequiredFor(self, name: str) -> ([str], None):
        return self.requiredFor.get(name, None)

    def __str__(self):
        return f'[TND] -> {[f"{e.Name}:{e.Type}"  for e in self.Entities.values()]}'
