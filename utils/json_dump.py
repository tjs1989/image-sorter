import json


def dump_to_file(data, out):
    json_out = json.dumps(data, indent=4)
    with open(out, 'w') as f:
        f.write(json_out)
