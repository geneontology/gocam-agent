import json
import os
import subprocess
import time

def call_generalist(prompt):
    # Instead of calling an external python script, we can write a script that runs the generalist agent via the gemini tool? 
    # Actually, we are running INSIDE the generalist agent essentially, but we can't call tools from a python script directly unless we use an API.
    # The instructions say "Actively ask Gemini subagents for help refining these processes". We can just use the `generalist` tool provided in our tool set!
    pass
