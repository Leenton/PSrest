PROCESS_SCHEMA = {
    "type" : "object",
    "properties" : {
        "ticket" : {
            "type" : "string",
            'minLength': 32,
            'maxLength': 32 # TODO : Make this a 4 byte integer with a max value of 2^32
        }
    },
    "required": ["ticket"],
    "additionalProperties": False
}

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

CONFIG_SCHEMA = {
    "type" : "object",
    "properties" : {
        "Hostname" : {"type" : "string"},
        "Port" : {"type" : "integer"},
        "Cert" : {"type" : "string"},
        "Repository" : {"type" : "string"},
        "DefaultTTL" : {"type" : "integer"},
        "MaxTTL" : {"type" : "integer"},
        "ArbitraryCommands" : {"type" : "boolean"},
        "Modules" : {"type" : "array", 'uniqueItems': True, "items": {"type": "string"}},
        "Enabled" : {"type" : "array", 'uniqueItems': True, "items": {"type": "string"}},
        "Disabled" : {"type" : "array", 'uniqueItems': True, "items": {"type": "string"}},
        "Help" : {"type" : "boolean"},
        "DefaultDepth" : {"type" : "integer"},
    },
    "required": [
        "Hostname",
        "Port",
        "Cert",
        "Repository",
        "DefaultTTL",
        "MaxTTL",
        "ArbitraryCommands",
        "Modules",
        "Enabled",
        "Disabled",
        "Help",
        "DefaultDepth"
        ],
    "additionalProperties": False
}