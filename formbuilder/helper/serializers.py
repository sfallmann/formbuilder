import json

def get_dict(obj):
    d = {}
    [
        d.update(
            {
                str(field.name): str(getattr(obj,field.name))
            }
        ) for field in obj._meta.fields
    ]
    return d


def get_json(obj):
    return json.dumps(
        get_dict(obj),sort_keys=True)
