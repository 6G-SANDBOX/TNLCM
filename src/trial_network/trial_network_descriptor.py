from json import loads

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

def check_component_descriptor(descriptor, component):
    for component_name, component_data in descriptor.items():
        return component_name == component and component_data is not None
    return False

def add_component_descriptor(descriptor, component_name, component_data):
    descriptor[component_name] = component_data
    return descriptor

def add_component_tn_vxlan(descriptor):
    if not check_component_descriptor(descriptor, "tn_vxlan"):
        component_data = {
            "public": {
                "one_vxlan_name": "tn_vxlan_review"
            }
        }
        return add_component_descriptor(descriptor, "tn_vxlan", component_data)

def add_component_tn_bastion(descriptor):
    if not check_component_descriptor(descriptor, "tn_bastion"):
        component_data = {
            "depends_on": ["tn_vxlan"],
            "public": None
        }
        return add_component_descriptor(descriptor, "tn_bastion", component_data)

def get_component_depends_on(component_data):
    return component_data["depends_on"]

def get_component_public(component_data):
    return component_data["public"]