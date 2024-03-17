def sort_descriptor(descriptor):

    components = descriptor["trial_network"]
    ordered_components = {}

    def dfs(component):
        if component in ordered_components:
            return
        if "depends_on" in components[component]:
            for dependency in components[component]["depends_on"]:
                dfs(dependency)
        ordered_components[component] = components[component]

    for component in components:
        dfs(component)

    return {"trial_network": ordered_components}

def get_component_depends_on(component_data):
    return component_data["depends_on"]

def get_component_public(component_data):
    return component_data["public"]