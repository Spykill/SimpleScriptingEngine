
import string
from math import *


class ScriptingEnvironment:

    def __init__(self):
        self.functions = {}
        self.global_fcns = {}
        self.global_vars = {}

        self.define_function("set", 2, f_set)
        self.define_function("gset", 2, f_gset)
        self.define_function("print", 1, f_print)
        self.define_function("if", 2, f_if)
        self.define_function("&", 3, f_and)
        self.define_function("|", 3, f_or)
        self.define_function("=", 3, f_equals)
        self.define_function("!", 2, f_not)
        self.define_function(".", 3, f_greater)
        self.define_function(">=", 3, f_greaterequal)
        self.define_function("<", 3, f_less)
        self.define_function("<=", 3, f_lessequal)
        self.define_function("slength", 3, f_slength)
        self.define_function("+", 3, f_add)
        self.define_function("-", 3, f_sub)
        self.define_function("*", 3, f_mul)
        self.define_function("/", 3, f_div)
        self.define_function("round", 2, f_rnd)
        self.define_function("floor", 2, f_flr)
        self.define_function("ceil", 2, f_ceil)
        self.define_function("define", 3, f_def)
        self.define_function("gdefine", 3, f_gdef)

    def define_function(self, fcn_name, param_count, tgt_fcn):
        """
        Defines this function to be able to be used in this environment

        @type fcn_name: str
        @type param_count: int
        @type tgt_fcn: function (ScriptingEnvironment, list[str])
        @rtype: bool
        """
        v = len(fcn_name)
        if fcn_name not in self.functions:
            self.functions[fcn_name] = FunctionDefinition(self, fcn_name, param_count, tgt_fcn)
            return True
        else:
            return False

    def execute_script(self, scope, src):
        """
        Executes the code defined in the src string based on the current environment

        @type scope: ScriptingScope
        @type src: str
        @rtype: ScriptingScope
        """

        if type(src) is not str:
            return None

        src = src.strip()

        while len(src) > 0:
            next_token = src[:src.find(' ')]
            fcn = None
            if next_token in self.functions:
                fcn = self.functions[next_token]
            elif next_token in scope.functions:
                fcn = scope.functions[next_token]
            elif next_token in self.global_fcns:
                fcn = self.global_fcns[next_token]
            elif next_token == 'return':
                scope.exit = True
                return ['return', scope]
            else:
                return ['invalid', scope]

            print(fcn.fcn_name, end='')

            src = src[len(next_token):].strip()
            params = []
            for i in range(0, fcn.param_count):
                if src[0] == '"':
                    v = src.find('"', 1)
                    while v != -1:
                        if src[v-1] == "\\":
                            v = src.find('"', v + 1)
                        else:
                            break
                    p = src[1:v]
                    params.append(p)
                    src = src[v+1:].strip()
                else:
                    ind = -1
                    for j in range(len(src)):
                        if src[j] in string.whitespace:
                            ind = j
                            break
                    p = src[:]
                    if ind != -1:
                        p = src[:ind]
                    print(' ' + p, end='')
                    src = src[len(p):].strip()
                    params.append(get_value(self, scope, p))
            print()
            fcn.invoke(scope, params)

            if scope.exit:
                return ['return', scope]

            src = src.strip()
        return ["eos", scope]


class ScriptingScope:
    def __init__(self):
        self.vars = {}
        self.functions = {}
        self.exit = False


def f_set(se, scope, params):
    var_name = params[0]
    if not is_valid_variable_name(var_name):
        error_message(scope, "Invalid variable name! Line: set " + params[0] + " " + params[1])
        return

    val = params[1]
    if val[0] == '#':
        val = get_variable(se, scope, val)
        if val is not None:
            scope.vars[var_name] = val
        else:
            error_message(scope, "Variable not defined! Line: set " + params[0] + " " + params[1])
            return
    else:
        scope.vars[var_name] = val


def f_gset(se, scope, params):

    print ("GSET " + params[0] + " " + params[1])
    var_name = params[0]
    if not is_valid_variable_name(var_name):
        error_message(scope, "Invalid variable name! Line: gset " + params[0] + " " + params[1])
        return

    val = params[1]
    if val[0] == '#':
        val = get_variable(se, scope, val)
        if val is not None:
            se.global_vars[var_name] = val
        else:
            error_message(scope, "Variable not defined! Line: gset " + params[0] + " " + params[1])
            return
    else:
        se.global_vars[var_name] = val
        print("GSET!")


def f_print(se, scope, params):
    var_name = params[0]
    if is_defined_variable(se, scope, var_name):
        val = get_variable(se, scope, var_name)
        print(val)
    else:
        error_message(scope, "Variable not defined! Line: print " + params[0] + " " + str(se.global_vars))


def f_if(se, scope, params):
    print("IF " + params[0] + " " + params[1])
    var_name = params[0]
    if is_defined_variable(se, scope, var_name):
        val = get_variable(se, scope, var_name)
        if val == 'true':
            se.execute_script(scope, step_into_code(params[1]))
    else:
        error_message(scope, 'Invalid variable name! Line: if ' + params[0] + ' ' + params[1])
        return


def f_and(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        if get_variable(se, scope, var1) == 'true' and get_variable(se, scope, var2) == 'true':
            scope.vars[var3] = 'true'
        else:
            scope.vars[var3] = 'false'
    else:
        error_message(scope, "Invalid variables! Line: & " + var1 + " " + var2 + " " + var3)
        return


def f_or(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        if get_variable(se, scope, var1) == 'true' or get_variable(se, scope, var2) == 'true':
            scope.vars[var3] = 'true'
        else:
            scope.vars[var3] = 'false'
    else:
        error_message(scope, "Invalid variables! Line: | " + var1 + " " + var2 + " " + var3)
        return


def f_equals(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            v1 = float(get_variable(se, scope, var1))
            v2 = float(get_variable(se, scope, var2))
            if v1 == v2:
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
        except ValueError:
            if get_variable(se, scope, var1) == get_variable(se, scope, var2):
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
    else:
        error_message(scope, "Invalid variables! Line: = " + var1 + " " + var2 + " " + var3)
        return


def f_not(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_defined_variable(se, scope, var1) and is_valid_variable_name(var2):
        if get_variable(se, scope, var1) == 'true':
            scope.vars[var2] = 'false'
        else:
            scope.vars[var2] = 'true'
    else:
        error_message(scope, "Invalid variables! Line: ! " + var1 + " " + var2)
        return


def f_greater(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            if float(get_variable(se, scope, var1)) > float(get_variable(se, scope, var2)):
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: > " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: > " + var1 + " " + var2 + " " + var3)
        return


def f_greaterequal(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            if float(get_variable(se, scope, var1)) >= float(get_variable(se, scope, var2)):
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: >= " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: >= " + var1 + " " + var2 + " " + var3)
        return


def f_less(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            if float(get_variable(se, scope, var1)) < float(get_variable(se, scope, var2)):
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: < " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: < " + var1 + " " + var2 + " " + var3)
        return


def f_lessequal(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            if float(get_variable(se, scope, var1)) <= float(get_variable(se, scope, var2)):
                scope.vars[var3] = 'true'
            else:
                scope.vars[var3] = 'false'
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: <= " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: <= " + var1 + " " + var2 + " " + var3)
        return


def f_slength(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_defined_variable(se, scope, var1) and is_valid_variable_name(var2):
        scope.vars[var2] = len(get_variable(se, scope, var1))
    else:
        error_message(scope, "Invalid variables! Line: slength " + var1 + " " + var2)
        return


def f_add(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        var1 = get_variable(se, scope, var1)
        var2 = get_variable(se, scope, var2)
        try:
            scope.vars[var3] = str((float(var1) + float(var2)))
        except ValueError:
            # error_message(scope, "Variables are not numbers!")
            scope.vars[var3] = var1 + var2
    else:
        error_message(scope, "Invalid variables! Line: + " + var1 + " " + var2 + " " + var3)
        return


def f_sub(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            scope.vars[var3] = str((float(get_variable(se, scope, var1)) - float(get_variable(se, scope, var2))))
        except ValueError:
            error_message(scope, "Variables are not numbers! " + get_variable(se, scope, var1) + " " + get_variable(se, scope, var2) + " Line: - " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: - " + var1 + " " + var2 + " " + var3)
        return


def f_mul(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            scope.vars[var3] = str((float(get_variable(se, scope, var1)) * float(get_variable(se, scope, var2))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: * " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: * " + var1 + " " + var2 + " " + var3)
        return


def f_div(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            scope.vars[var3] = str((float(get_variable(se, scope, var1)) / float(get_variable(se, scope, var2))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: / " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: / " + var1 + " " + var2 + " " + var3)
        return


def f_mod(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_defined_variable(se, scope, var1) and is_defined_variable(se, scope, var2) and is_valid_variable_name(var3):
        try:
            scope.vars[var3] = str((float(get_variable(se, scope, var1)) % float(get_variable(se, scope, var2))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: % " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variables! Line: % " + var1 + " " + var2 + " " + var3)
        return


def f_rnd(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_defined_variable(se, scope, var1) and is_valid_variable_name(var2):
        try:
            scope.vars[var2] = str(round(float(get_variable(se, scope, var1))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: round " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variables! Line: round " + var1 + " " + var2)
        return


def f_flr(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_defined_variable(se, scope, var1) and is_valid_variable_name(var2):
        try:
            scope.vars[var2] = str(floor(float(get_variable(se, scope, var1))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: floor " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variables! Line: floor " + var1 + " " + var2)
        return


def f_ceil(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_defined_variable(se, scope, var1) and is_valid_variable_name(var2):
        try:
            scope.vars[var2] = str(ceil(float(get_variable(se, scope, var1))))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: ceil " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variables! Line: ceil " + var1 + " " + var2)
        return


def f_def(se, scope, params):
    var_name = params[0]
    if contains_any(var_name, string.whitespace):
        error_message(scope, "Invalid function name! Line: define " + params[0] + " " + params[1] + " " + params[2])
        return

    try:
        param_count = int(params[1])
    except ValueError:
        error_message(scope, "Invalid parameter count! Line: define " + params[0] + " " + params[1] + " " + params[2])
        return
    val = params[2]
    if val[0] == '#':
        if is_defined_variable(se, scope, val):
            scope.functions[var_name] = CustomFunctionDefinition(se, var_name, param_count, get_variable(se, scope, val))
        else:
            error_message(scope, "Variable not defined! Line: define " + params[0] + " " + params[1])
            return
    else:
        scope.functions[var_name] = CustomFunctionDefinition(se, var_name, param_count, val)


def f_gdef(se, scope, params):
    var_name = params[0]
    if contains_any(var_name, string.whitespace):
        error_message(scope, "Invalid function name! Line: gdefine " + params[0] + " " + params[1] + " " + params[2])
        return

    try:
        param_count = int(params[1])
    except ValueError:
        error_message(scope, "Invalid parameter count! Line: gdefine " + params[0] + " " + params[1] + " " + params[2])
        return
    val = params[2]
    if val[0] == '#':
        if is_defined_variable(se, scope, val):
            se.global_fcns[var_name] = CustomFunctionDefinition(se, var_name, param_count, get_variable(se, scope, val))
        else:
            error_message(scope, "Variable not defined! Line: gdefine " + params[0] + " " + params[1])
            return
    else:
        se.global_fcns[var_name] = CustomFunctionDefinition(se, var_name, param_count, val)


def step_into_code(src):
    return src.replace('\\"', '"')


def is_valid_variable_name(var_name):
    return var_name[0] == '#' and not contains_any(var_name, string.whitespace)


def is_defined_variable(se, scope, var_name):
    return var_name[0] == '#' and not contains_any(var_name, string.whitespace) and (var_name[1:] in se.global_vars or var_name[1:] in scope.vars)


def get_value(se, scope, var_name):
    if var_name[0] == '$' and not contains_any(var_name, string.whitespace) and (var_name[1:] in se.global_vars or var_name[1:] in scope.vars):
        return get_variable(se, scope, var_name)
    else:
        return var_name


def get_variable(se, scope, var_name):
    if var_name[1:] in se.global_vars:
        return se.global_vars[var_name[1:]]
    elif var_name[1:] in scope.vars:
        return scope.vars[var_name[1:]]
    else:
        return None


def contains_any(s, chars):
    """Check whether 's' contains ANY of the chars in 'chars'"""
    return 1 in [c in s for c in chars]


def contains_all(s, chars):
    """Check whether 's' contains ALL of the chars in 'chars'"""
    return 0 not in [c in s for c in chars]


def error_message(scope, msg):
    scope.exit = True
    print("=====================================" + msg)


class FunctionDefinition:

    def __init__(self, env, fcn_name, param_count, tgt_fcn):
        """
        @type env: ScriptingEnvironment
        @type fcn_name: str
        @type param_count: int
        @type tgt_fcn: function (ScriptingEnvironment, list[str])
        """

        self.env = env
        self.fcn_name = fcn_name
        self.param_count = param_count
        self.tgt_fcn = tgt_fcn

    def invoke(self, scope, params):
        """
        Triggers this function with the given parameters
        @type scope: ScriptingScope
        @type params: list[str]
        @rtype: None
        """
        self.tgt_fcn(self.env, scope, params)


class CustomFunctionDefinition(FunctionDefinition):

    def invoke(self, scope, params):
        fcn_scope = ScriptingScope()
        for i in range(self.param_count):
            fcn_scope.vars['#PARAM' + str(i)] = params[i]
        self.env.execute_script(fcn_scope, self.tgt_fcn.replace('\\"', '"'))
