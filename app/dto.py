from pydantic import BaseModel


class Input(BaseModel):
    """
    Data Transfer Object for input data.

    This class represents the input data structure used in the create_message
    function. It contains a single field:
    
    Attributes:
        input (str): The input message content provided by the user.
    """
    input: str
