from pydantic import create_model, Field
from typing import List, Dict, Any, Literal, get_args, get_origin
import ast

from components import types

import openai
import instructor

import os

from dotenv import load_dotenv

load_dotenv()

def create_dynamic_model(fields: List[Dict[str, Any]]):
    """
    Create a Pydantic model dynamically based on the provided fields.
    """
    
    field_definitions = {}
    for field in fields:
        name = field['name']
        field_type = field['field_type']
        
        # validation to ensure no arbitrary code can be executed.
        if field_type not in [t for t,_ in types]:
            raise ValueError(f"Invalid field type '{field_type}' for field '{name}'")
        
        # Handle Literal type
        if isinstance(field_type, str) and field_type.startswith('Literal['):
            # Parse the Literal values
            literal_values = ast.literal_eval(field_type[len('Literal['):-1])
            
            if not isinstance(literal_values, (list, tuple)):
                literal_values = [literal_values]
                
            # Determine the type of the first value to infer the Literal type
            first_value_type = type(literal_values[0])
            
            if not all(isinstance(value, first_value_type) for value in literal_values):
                raise ValueError(f"All values in Literal field '{name}' must be of type {first_value_type}")
            
            field_type = Literal[tuple(literal_values)]
        elif isinstance(field_type, str):
            # Convert other string types to actual Python type
            field_type = eval(field_type)
        
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