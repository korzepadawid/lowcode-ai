CSHARP_DATATYPES = [
    "Byte",
    "Sbyte",
    "Short",
    "Ushort",
    "Int",
    "Uint",
    "Long",
    "Ulong",
    "Float",
    "Double",
    "Decimal",
    "Char",
    "Bool",
    "String",
    "Object",
    "Dynamic",
    "Void",
    "DateTime"
]

def parse_context_fields(context: dict) -> str:
    """ Parse context data fields.
        Approach 2: Using hardcoded data types.
        Assumptions (may need corrections):
        - if dataType is a predefined dataType, it is a simple datatype (str,int,etc)
        - if dataType is not simple and children are empty and dataTypeComponents exist, it is a structure
        - if dataType is not simple and children are empty and dataTypeComponents dont exist, it is a table (without fields)
        - if dataType is not simple and children exist and dataTypeComponents exist, it is a structure
        - if dataType is not simple and children exist and dataTypeComponents dont exist, it is a table (with defined fields)
        - structure always have non-empty dataTypeComponents
    """
    fields_processed = []
    try:
        fields = context["fields"]
        print(fields)
        for field in fields:
            if field["dataType"] in CSHARP_DATATYPES:
                fields_processed.append(f"PF.{field["symbol"]}: {field["dataType"]}")
            else:
                structure = field["dataType"].split(".")[-1]
                if not field["children"]:
                    if field["dataTypeComponents"]:
                        for component in field["dataTypeComponents"]:
                            fields_processed.append(f"PF.{structure}.{component['symbol']}: {component['type']}")
                    else:
                        fields_processed.append(f"PF.{structure}: Table")
                else:
                    if field["dataTypeComponents"]:
                        for component in field["dataTypeComponents"]:
                            fields_processed.append(f"PF.{structure}.{component['symbol']}: {component['type']}")
                    else:
                        fields_processed.append(f"PF.{structure}: Table")
                        for child in field["children"][0]["children"]:
                            fields_processed.append(f" * {child["symbol"]}: Str")
    except Exception as e:
        fields_processed.append(f"Data model not available due to error: {str(e)}. Ask user to provide data model.")

    fields_processed_joined = "\n".join(fields_processed)

    return fields_processed_joined


def parse_context_screens(context: dict) -> str:
    """Parse screens from context."""

    screens_processed = []
    try:
        screens = context["screens"]
        print(screens)
        for screen in screens:
            screens_processed.append(f"{screen["symbol"]} (alias:{screen['name']})")

    except Exception as e:
        screens_processed.append(
            f"Screens not available due to error: {str(e)}. Ask user to provide available screens.")

    screens_processed_joined = "\n".join(screens_processed)

    return screens_processed_joined