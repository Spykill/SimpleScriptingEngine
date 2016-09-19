# SimpleScriptingEngine
A simple scripting engine that allows you to easily define your own functions for use within a script

Simply run main.py in Python to run script.ssf

# SimpleScript Language Rules:

All lines in SimpleScript begin with a function name. For example:

	set

After the function name, you must put a valid number of parameters for the function. For example, "set" has 2 parameters. Parameters must either be a value or a variable. To pass a value to the function, simply type in the value. If the value has spaces, surround it in quotation marks. If the value has quotation marks around it, but contains quotation marks within it, use backslash (\) to escape it. Just remember to add an extra backslash for each layer deep you go, if you are writing code.

	set #this "test stuff! \""

Once a variable is set, it may be used as its value by prefacing it with a dollar sign ($).

	set #other $this

When a function asks for a variable name, it must begin with a pound (#).

There are many functions to play with. In fact, the 'define' and 'gdefine' functions allow you to define your own functions in your code.

SimpleScript does have scope, although simplified. There is a local scope and a global scope. Scope is not layered. This means that when calling the 'if' function, any variables defined in the if will remain once the if has ended.

If you want more detail as to what functions there are, just look at either script.ssf (just an example script) or ScriptingAPI.pi. Good luck!
