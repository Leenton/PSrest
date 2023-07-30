RUN_SCHEMA = {
    "type" : "object",
    "properties" : {    
        "cmdlet" : {"type" : "string"},
        "parameters" : {"type" : ["object", "array"], "optional": True},
    },
}