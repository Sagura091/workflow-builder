# backend/plugins/uppercase.py
def run(inputs, config):
    text = inputs.get("text", "")
    return {"result": str(text).upper()}

def generate_code(config):
    return "result = text.upper()"
