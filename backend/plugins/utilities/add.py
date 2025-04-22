# backend/plugins/add.py
__plugin_meta__ = {
    "name": "Add",
    "category": "Math",
    "description": "Adds two numbers",
    "editable": True,
    "generated": False,
    "inputs": {
        "a": "number",
        "b": "number"
    },
    "outputs": {
        "sum": "number"
    },
    "configFields": []
}

def run(inputs, config):
    a = float(inputs.get("a", 0))
    b = float(inputs.get("b", 0))
    return {"sum": a + b}

def generate_code(config):
    return "sum = a + b"
