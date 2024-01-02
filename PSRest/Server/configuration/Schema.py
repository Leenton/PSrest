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
        "parameters" : {"type" : ["object", "array"]},
        "array_wrap" : {"type" : "boolean", "optional": True}
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
        "Port" : {
            "type" : "integer",
            "maximum": 65535,
            "minimum": 1
        },
        "SSLCertificate" : {"type" : ["string", "null"]},
        "SSLKeyFile" : {
            "type" : ["string", "null"],
            "required": ["SSLCertificate"],
        },
        "SSLKeyFilePassword" : {
            "type" : ["string", "null"],
            "required": ["SSLCertificate", "SSLKeyFile"],
        },
        "SSLCiphers" : {
            "enum": [
                "TLSv1",
                "TLSv1.1",
                "TLSv1.2",
                "TLSv1.3"
            ]
        },
        "DefaultTTL" : {
            "type" : "integer",
            "maximum": 604800,
            "minimum": 1
        },
        "StrictTTL" : {"type" : "boolean"},
        "MaxTTL" : {
            "type" : "integer",
            "maximum": 604800,
            "minimum": 1
        },
        "ArbitraryCommands" : {"type" : "boolean"},
        "Help" : {"type" : "boolean"},
        "Docs" : {"type" : "boolean"},
        "DefaultDepth" : {
            "type" : "integer",
            "maximum": 100,
        },
        "StrictDepth" : {"type" : "boolean"},
    },
    "required": [
        "Port",
        "DefaultTTL",
        "MaxTTL",
        "StrictTTL",
        "ArbitraryCommands",
        "Help",
        "Docs",
        "DefaultDepth",
        "StrictDepth"
        ],
    "additionalProperties": False
}
