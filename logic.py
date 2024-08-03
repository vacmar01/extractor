from pydantic import create_model, Field
from typing import List, Dict, Any, Literal, Optional, get_args, get_origin
import ast

from components import types

import openai
import instructor

import os

from dotenv import load_dotenv

load_dotenv()

ALLOWED_TYPES = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'List[str]': List[str],
    'List[int]': List[int],
    'List[float]': List[float],
    'Optional[str]': Optional[str],
    'Optional[int]': Optional[int],
    'Optional[float]': Optional[float],
}

def parse_literal(literal_str: str):
    # Remove 'Literal' and brackets
    values_str = literal_str[7:-1]
    
    # Parse the values
    try:
        values = eval(values_str, {'__builtins__': {}}, {})
    except:
        raise ValueError(f"Invalid Literal format: {literal_str}")
    
    if not isinstance(values, (list, tuple)):
        values = (values,)
    
    # Ensure all values are of the same type
    value_type = type(values[0])
    if not all(isinstance(v, value_type) for v in values):
        raise ValueError("All values in Literal must be of the same type")
    
    return Literal[values]

def get_field_type(type_str: str) -> Any:
    if type_str in ALLOWED_TYPES:
        return ALLOWED_TYPES[type_str]
    elif type_str.startswith('Literal['):
        return parse_literal(type_str)
    else:
        raise ValueError(f"Unsupported type: {type_str}")

def create_dynamic_model(fields: List[Dict[str, Any]]):
    """
    Create a Pydantic model dynamically based on the provided fields.
    """
    
    field_definitions = {}
    for field in fields:
        name = field['name']
        field_type_str = field['field_type']
        
        try:
            field_type = get_field_type(field_type_str)
        except ValueError as e:
            raise ValueError(f"Invalid field type for '{name}': {str(e)}")
        
        # Add any additional field parameters
        field_params = {k: v for k, v in field.items() if k not in ['name', 'type']}
        
        field_definitions[name] = (field_type, Field(**field_params))
    
    # Create and return the dynamic model
    DynamicModel = create_model('DynamicModel', **field_definitions)
    return DynamicModel

client = openai.OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1",
)

# By default, the patch function will patch the ChatCompletion.create and ChatCompletion.create methods to support the response_model parameter
client = instructor.from_openai(client, mode=instructor.Mode.JSON)

def extract(text, ReturnModel):
    """
    Extract information from the provided text using the specified model schema and return the results as a Pydantic model.
    """
    
    return client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        response_model=ReturnModel,
        messages=[
            {"role": "user", "content": f"Extract {text}"},
        ],
    )