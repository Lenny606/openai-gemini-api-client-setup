tool_structure = {
    "name": "tool_name",
    "description": "Clear, concise description of what the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of param1"
            },
            "param2": {
                "type": "integer",
                "description": "Description of param2",
                "minimum": 0
            },
            "optional_param": {
                "type": "boolean",
                "description": "Optional flag",
                "default": False
            }
        },
        "required": ["param1"]
    }
}
