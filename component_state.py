import tkinter as tk
import json

# Mapping of component types to their state retrieval functions
state_map = {
    tk.Entry: lambda comp: {"name": comp.unique_name, "type": "Entry", "state": comp.get()},
    tk.Checkbutton: lambda comp: {"name": comp.unique_name, "type": "Checkbutton", "state": comp.var.get()},
    tk.Radiobutton: lambda comp: {"name": comp.unique_name, "type": "Radiobutton", "state": comp.var.get()},
    tk.BooleanVar: lambda comp: {"name": comp.unique_name, "type": "BooleanVar", "state": comp.get()},
    tk.Text: lambda comp: {"name": comp.unique_name, "type": "Text", "state": comp.get("1.0", tk.END)}
}


# Function to get the state of a component
def get_component_state(component):
    for comp_type, state_func in state_map.items():
        if isinstance(component, comp_type):
            return state_func(component)
    return {}


# Function to save the state of components to a JSON file
def save_components_state(components, file_name):
    components_state = []
    for i, component in enumerate(components):
        component.unique_name = f"component_{i}"  # Assign unique name
        state = get_component_state(component)
        if state:
            components_state.append(state)
    with open(file_name, 'w') as f:
        json.dump(components_state, f, indent=4)


# Helper function to apply a saved state to a single component
def _apply_component_state(component, state):
    #omponent_name = state["name"]
    if state["type"] == "Entry":
        component.delete(0, tk.END)
        component.insert(0, state["state"])
    elif state["type"] == "Checkbutton":
        component.var.set(state["state"])
    elif state["type"] == "Radiobutton":
        component.var.set(state["state"])
    elif state["type"] == "BooleanVar":
        component.set(state["state"])
    elif state["type"] == "Text":
        component.delete("1.0", tk.END)
        component.insert("1.0", state["state"])


# Original function to load the state of components from a JSON file
def load_components_state(components, file_name):
    try:
        with open(file_name, 'r') as f:
            components_state = json.load(f)
    except FileNotFoundError:
        return
    for i, component in enumerate(components):
        if any(isinstance(component, comp_type) for comp_type in state_map):
            component.unique_name = f"component_{i}"
    name_map = {component.unique_name: component for component in components if hasattr(component, 'unique_name')}
    for state in components_state:
        component_name = state["name"]
        if component_name in name_map:
            _apply_component_state(name_map[component_name], state)