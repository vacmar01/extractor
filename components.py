from fasthtml.common import *
from fasthtml.components import ft_hx, Svg

types = [
    ("str", "Text"),
    ("int", "Integer"),
    ("float", "Floating point number"),
    ("bool", "Boolean"),
    ("Literal", "Enumeration"),
    ("List[str]", "List of Text"),
    ("List[int]", "List of Integers"),
]

js = """
me('#field_type').on('change', function() {
    if (me('#field_type').value == 'Literal') {
        me('#options-wrapper').classRemove('d-none');
    } else {
        me('#options-wrapper').classAdd('d-none');
    }
});
"""

def ft_Path(*args, **kwargs):
    return ft_hx('path', *args, **kwargs)

def hero():
    return Div(
        Span("🛠️", cls='d-block mx-auto mb-4', style="font-size: 8rem;"),
        H1('Extract0r', cls='display-5 fw-bold text-body-emphasis'),
        Div(
            P('Enter some text and what data you want to extract from it and let the LLM magic to it\'s thang.', cls='lead mb-4'),
            Div(
                Button(
                    chevron_down_icon(),
                    'Get Started', 
                    Script("me().on('click', e => { me('#main-content').scrollIntoView({behavior: 'smooth'}); })"),
                    type='button', 
                    cls='btn btn-primary btn-lg px-4 gap-3'),
                cls='d-grid gap-2 d-sm-flex justify-content-sm-center'
            ),
            cls='col-lg-6 mx-auto'
        ),
        cls='px-4 py-5 my-5 text-center'
    )

def chevron_down_icon():
    return Svg(
        ft_Path(stroke_linecap='round', stroke_linejoin='round', d='m19.5 8.25-7.5 7.5-7.5-7.5'),
        xmlns='http://www.w3.org/2000/svg',
        fill='none',
        viewbox='0 0 24 24',
        stroke_width='1.5',
        stroke='currentColor',
        cls="d-inline-block",
        style="width: 1.25rem;"
    )

def clipboard_icon():
    return Svg(
        ft_Path(stroke_linecap='round', stroke_linejoin='round', d='M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184'),
        xmlns='http://www.w3.org/2000/svg',
        fill='none',
        viewbox='0 0 24 24',
        stroke_width='1.5',
        stroke='currentColor',
        cls="d-inline-block",
        style="width: 1rem;"
    )

def spinner(): 
    return Span(role='status', aria_hidden='true', cls='spinner-border spinner-border-sm htmx-indicator', id='indicator')

def submit_button(oob=False, disabled=True):
    return Button(
        spinner(), 
        Span('Submit'), 
        type='submit', 
        cls="btn btn-primary", 
        id="submit-text", 
        disabled=disabled, 
        hx_swap_oob=str(oob).lower(),
    ),
    
def copy_button():
    copy_to_clipboard = Script("""
        function copyToClipboard() {
            let text = me('#result-json').innerText;
            
            navigator.clipboard.writeText(text).then(function() {
                console.log('Copying to clipboard was successful!');
                alert('Copied to clipboard');
            }, function(err) {
                console.error('Async: Could not copy text: ', err);
            });
        }
    """)
    
    return Button(Div(clipboard_icon(), 'Copy', clas="d-flex items-center"), copy_to_clipboard, onclick="copyToClipboard()", cls="btn btn-primary btn-sm")

def schema_form(): 
    return  Form(
                Div(
                    Label("Field Name (only letters and '_')", fr="name"),
                    Input(id="name", cls="form-control", ),
                    cls="mb-3"
                ),
                Div(
                    Label("Type of field", fr="field_type"),
                    Select(
                        *[Option(txt, value=val) for val,txt in types],
                        Script(code=js),
                        cls="form-select",
                        id="field_type",
                    ),
                    cls="mb-3"
                ),
                Div(Input(placeholder="options (separated by comma)", id="options", cls="form-control"), cls="mb-3 d-none", id="options-wrapper"),
                Button(spinner(), 'Add', type='submit', cls="btn btn-primary"),
                hx_post='/add_field',
                target_id="schema",
                hx_disabled_elt="find button"
            )
    
def schema_list(schema):
    return Ul(
        *[Li(
            f"{field['name']}: {field['field_type']} | ", 
            A('delete',
                hx_delete=f"/delete/{field['id']}",
                target_id=f"field-{field['id']}",
                hx_swap="outerHTML",
                hx_confirm="Are you sure you want to delete this field?",
            ), 
            cls="my-2",
            id=f"field-{field['id']}") for field in schema]
    )
    
def footer(): 
    return Div(
        P(
            "Made with ❤️ by ",
            A("Marius Vach", href="mailto:mariusvach@gmail.com", target="_blank"),
            " using ",
            A("FastHTML", href="https://fastht.ml", target="_blank"),
            ".",
            cls="text-center"
        ),
        cls="container py-4"
    )