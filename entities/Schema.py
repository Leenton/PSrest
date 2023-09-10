RUN_SCHEMA = {
    "type" : "object",
    "properties" : {    
        "cmdlet" : {"type" : "string"},
        "parameters" : {"type" : ["object", "array"]}
    },
    "required": ["cmdlet"],
    "additionalProperties": False
}

OAUTH_SCHEMA = {
    "type" : "object",
    "properties" : {
        "client_id" : {"type" : "string", "optional": True},
        "client_secret" : {"type" : "string", "optional": True},
        "refresh_token" : {"type" : "string", "optional": True},
        "grant_type" : {"enum": [
            "client_credential",
            "refresh_token"
            ]},
    },
    "required": ["grant_type"],
    "additionalProperties": False,
    "if": {
        "properties": {
            "grant_type": {"const": "refresh_token"}
        },
    },
    "then": {
        "required": ["refresh_token"]
    },
    "else": {
        "required": ["client_id", "client_secret"]
    }
}