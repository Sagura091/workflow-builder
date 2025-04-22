# backend/plugins/logger.py
__plugin_meta__ = {
    "name": "Logger",
    "category": "System",
    "description": "Logs and returns the input value",
    "editable": True,
    "generated": False,
    "inputs": { "value": "any" },
    "outputs": {},
    "configFields": []
}

def run(inputs, config):
    value = inputs.get("value")
    print("[Logger]", value)
    return {"logged": value}

def generate_code(config):
    return "print(value)"
