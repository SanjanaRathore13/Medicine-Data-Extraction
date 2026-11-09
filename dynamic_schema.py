
import json


def create_dynamic_schema(additional_attributes):
    """
    Prepare additional medicine attributes
    in JSON format for database storage.
    """

    if not isinstance(additional_attributes, dict):
        raise TypeError(
            "Additional attributes must be a dictionary."
        )

    dynamic_data = {}

    for attribute, value in additional_attributes.items():

        if attribute and value is not None:

            attribute_name = attribute.strip().lower()

            if attribute_name:
                dynamic_data[attribute_name] = value

    return dynamic_data


def convert_to_json(dynamic_data):
    """
    Convert dynamic attributes into JSON string.
    """

    json_data = json.dumps(
        dynamic_data,
        ensure_ascii=False
    )

    return json_data


def read_dynamic_attributes(json_data):
    """
    Convert JSON string back into Python dictionary.
    """

    if not json_data:
        return {}

    return json.loads(json_data)
