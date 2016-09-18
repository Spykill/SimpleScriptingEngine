from ScriptingAPI import ScriptingEnvironment, ScriptingScope

se = ScriptingEnvironment()

with open('script.ssf') as open_file:
    se.execute_script(ScriptingScope(), open_file.read())

