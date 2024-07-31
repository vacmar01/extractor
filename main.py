import uuid
from fasthtml.common import *

from components import submit_button, schema_form, schema_list, copy_button, footer, hero

from logic import create_dynamic_model, extract

custom_style = Style("""
    .htmx-indicator{
        display:none;
    }
    .htmx-request .htmx-indicator{
        display:inline-block;
    }
    .htmx-request.htmx-indicator{
        display:inline-block;
    }
""")

bootstrap = Link(href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css', rel='stylesheet', integrity='sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC', crossorigin='anonymous')

app, rt = fast_app(pico=False, live=False, hdrs=(bootstrap, custom_style))

@rt('/')
def get(session):
    if 'json_schema' not in session:
        session['json_schema'] = []
        
    json_schema = session['json_schema']
    
    return Div(
        hero(),
        # H1("Extraction Tool"),
        # P("Enter text on the left and define the schema of the data you want to extract on the right. The tool will extract the information from the text and display it below."),
        Hr(),
        Div(
            Div(
                H2("Text"),
                P("Enter the text you want to extract information from here."),
                Form(
                    Textarea(rows=20, style="width: 100%", id="text", cls="form-control mb-3"), 
                    submit_button(),
                    Script("me().on('submit', e => { me('#submit-text').disabled=true})"),
                    hx_post='/extract',
                    hx_target='#output',
                    hx_indicator="#indicator"
                ), 
                cls="col-md"
            ),
            Div(
                H2("Schema"),
                P("Define the schema of the information you want to extract here."),
                Div(
                    schema_form(),
                    id="schema-form",
                    cls="mb-3"
                ),
                Div(
                    schema_list(json_schema), 
                    id="schema", 
                    cls="mt-3"
                ),
                cls="col-md"
            ),
            cls="row mb-3",
            id="main-content"
        ),
        Div(
            id="output"
        ),
        footer(),
        cls="container py-4",
    )

@rt('/extract')
def post(text: str):
    try:
        ReturnModel = create_dynamic_model(json_schema)
    except Exception as e:
        return Div(
            Div(
                Div(H4("Error", cls='card-title'), copy_button(), cls="d-flex justify-content-between"),
                P(str(e), cls='card-text'),
                cls='card-body'
            ),
            cls='card'
        ), submit_button(oob=True, disabled=False)
        
    result = extract(text, ReturnModel)
    
    outp = Div(
        Div(
            Div(H4("Output", cls='card-title'), copy_button(), cls="d-flex justify-content-between"),
            P(Pre(result.model_dump(), id="result-json"), cls='card-text'),
            cls='card-body'
        ),
        cls='card'
    )
    return outp, submit_button(oob=True, disabled=False),

    
@rt('/add_field')
def post(session, name: str, field_type: str, options: str = None):
    
    json_schema = session['json_schema']
    
    if field_type == "Literal":
        options = options.split(",")
        options_string = ", ".join([f"'{o.strip()}'" for o in options])
        field_type = f"Literal[{options_string}]"
    
    o = {
        "name": name,
        "field_type": field_type
    }
    
    json_schema.append(o)
    
    #update the session with the new schema
    session['json_schema'] = json_schema
    
    return H3("Current Schema"), schema_list(json_schema), Div(schema_form(), id="schema-form", hx_swap_oob="true"), submit_button(disabled=False, oob=True) 

@rt('/delete/{name}')
def delete(session, name: str):
    json_schema = session['json_schema']
    json_schema = [field for field in json_schema if field['name'] != name]
    session['json_schema'] = json_schema

serve()