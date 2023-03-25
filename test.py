import json
data = {
    "foreground" : "red",
    "background" : "blue",
    "object" : "THIS IS A SAMPLE STRING"
}

data = [
    "red",
    "blue",
    "THIS IS A SAMPLE STRING"
]

parameter = "THIS IS A SAMPLE STRING"
print(json.dumps({"string" : parameter}))
