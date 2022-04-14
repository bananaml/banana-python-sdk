from .generics import run_main, start_main, check_main

# Generics
def run(api_key, model_key, model_inputs):
    out = run_main(
        api_key = api_key, 
        model_key = model_key, 
        model_inputs = model_inputs
    )
    return out

def start(api_key, model_key, model_inputs):
    out = start_main(
        api_key = api_key, 
        model_key = model_key, 
        model_inputs = model_inputs
    )
    return out
    
def check(api_key, call_id):
    out_dict = check_main(
        api_key = api_key,
        call_id = call_id
    )
    return out_dict