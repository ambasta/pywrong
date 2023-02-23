from typing import Any


def to_underscore_case(data: Any, convert: bool = True) -> Any:
    ret_val = type(data)()

    if isinstance(data, dict):
        ret_val = {
            to_underscore_case(key): to_underscore_case(value, False)
            for (key, value) in data.items()
        }
    elif isinstance(data, list):
        ret_val = [to_underscore_case(item, False) for item in data]
    elif convert and isinstance(data, str):
        ret_val = data.replace('-', '_').replace(' ', '_')
        ret_val = ''.join(
            [f'_{chr.lower()}' if chr.isupper() else chr for chr in ret_val]
        )

        if ret_val.startswith('_'):
            ret_val = ret_val[1:]
    return ret_val
