# backend/utils/plugin_template_generator.py
def generate_plugin_template(name: str, inputs: dict, outputs: dict, description: str = "Describe your plugin") -> str:
    return f'''__plugin_meta__ = {{
    "name": "{name}",
    "category": "Custom",
    "description": "{description}",
    "editable": True,
    "generated": True,
    "inputs": {inputs},
    "outputs": {outputs},
    "configFields": []
}}

def run(inputs, config):
    # Your logic here
    return {{}}

def generate_code(config):
    return "# Generated code placeholder"
'''

# Example usage:
# print(generate_plugin_template("Multiply", {"a": "number", "b": "number"}, {"result": "number"}))