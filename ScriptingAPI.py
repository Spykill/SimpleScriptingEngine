
import string
from math import *


class ScriptingEnvironment:

    def __init__(self):
        self.functions = {}
        self.global_fcns = {}
        self.global_vars = {}

        self.define_function("//", 1, False, f_comment)
        # [var_name, value to set]
        self.define_function("set", 2, False, f_set)
        # [var_name, value to set]
        self.define_function("gset", 2, False, f_gset)
        # [value to print]
        self.define_function("print", 1, False, f_print)
        # [value to print]
        self.define_function("println", 1, False, f_println)
        # [bool value (do the code), script]
        self.define_function("if", 2, False, f_if)
        # [bool value (do the code), scripts]
        self.define_function("while", 2, False, f_while)
        # [bool value 1, bool value 2, out var]
        self.define_function("&", 3, False, f_and)
        # [bool value 1, bool value 2, out var]
        self.define_function("|", 3, False, f_or)
        # [value 1, value 2, out var]
        self.define_function("=", 3, False, f_equals)
        # [value 1, out var]
        self.define_function("!", 2, False, f_not)
        # [value 1, value 2, out var]
        self.define_function(">", 3, False, f_greater)
        # [value 1, value 2, out var]
        self.define_function(">=", 3, False, f_greaterequal)
        # [value 1, value 2, out var]
        self.define_function("<", 3, False, f_less)
        # [value 1, value 2, out var]
        self.define_function("<=", 3, False, f_lessequal)
        # [string, out var]
        self.define_function("slength", 3, False, f_slength)
        # [value 1, value 2, out var]
        self.define_function("+", 3, False, f_add)
        # [value 1, value 2, out var]
        self.define_function("-", 3, False, f_sub)
        # [value 1, value 2, out var]
        self.define_function("*", 3, False, f_mul)
        # [value 1, value 2, out var]
        self.define_function("/", 3, False, f_div)
        # [value 1, out var]
        self.define_function("round", 2, False, f_rnd)
        # [value 1, out var]
        self.define_function("floor", 2, False, f_flr)
        # [value 1, out var]
        self.define_function("ceil", 2, False, f_ceil)
        # [value 1, out var]
        self.define_function("floattoint", 2, False, f_floattoint)
        # [string, index, out var]
        self.define_function("charat", 3, False, f_charat)
        # [char, out var]
        self.define_function("chartoint", 2, False, f_chartoint)
        # [string, start, end, out var]
        self.define_function("substr", 4, False, f_substr)
        # [fcn_name, param_count, will create new scope, code]
        self.define_function("define", 4, False, f_def)
        # [fcn_name, param_count, will create new scope, code]
        self.define_function("gdefine", 4, False, f_gdef)
        # [will create new scope, code]
        self.define_function("exec", 2, False, f_exec)

    def define_function(self, fcn_name, param_count, new_scope, tgt_fcn):
        """
        Defines this function to be able to be used in this environment

        @type fcn_name: str
        @type param_count: int
        @type new_scope: bool
        @type tgt_fcn: function (ScriptingEnvironment, list[str])
        @rtype: bool
        """
        v = len(fcn_name)
        if fcn_name not in self.functions:
            self.functions[fcn_name] = FunctionDefinition(self, fcn_name, param_count, new_scope, tgt_fcn)
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
            ind = src.find(' ')
            if ind == -1:
                next_token = src
            else:
                next_token = src[:ind]
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
                    src = src[len(p):].strip()
                    params.append(get_value(self, scope, p))
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


def f_comment(se, scope, params):
    pass


def f_set(se, scope, params):
    var_name = params[0]
    if not is_valid_variable_name(var_name):
        error_message(scope, "Invalid variable name! Line: set " + params[0] + " " + params[1])
        return

    scope.vars[var_name[1:]] = params[1]


def f_gset(se, scope, params):
    var_name = params[0]
    if not is_valid_variable_name(var_name):
        error_message(scope, "Invalid variable name! Line: gset " + params[0] + " " + params[1])
        return

    se.global_vars[var_name[1:]] = params[1]


def f_print(se, scope, params):
    print(params[0], end='')


def f_println(se, scope, params):
    print(params[0])


def f_if(se, scope, params):
    if params[0] == 'true':
        se.execute_script(scope, step_into_code(params[1]))


def f_while(se, scope, params):
    if is_defined_variable(se, scope, params[0]):
        while get_value(se, scope, '$' + params[0][1:]) == 'true':
            se.execute_script(scope, step_into_code(params[1]))
    else:
        error_message(scope, "Invalid variable! Line: while " + params[0] + " " + params[1])


def f_and(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        if var1 == 'true' and var2 == 'true':
            scope.vars[var3[1:]] = 'true'
        else:
            scope.vars[var3[1:]] = 'false'
    else:
        error_message(scope, "Invalid variable name! Line: & " + var1 + " " + var2 + " " + var3)


def f_or(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        if var1 == 'true' or var2 == 'true':
            scope.vars[var3[1:]] = 'true'
        else:
            scope.vars[var3[1:]] = 'false'
    else:
        error_message(scope, "Invalid variable name! Line: | " + var1 + " " + var2 + " " + var3)


def f_equals(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            v1 = float(var1)
            v2 = float(var2)
            if v1 == v2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
        except ValueError:
            if var1 == var2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
    else:
        error_message(scope, "Invalid variable name! Line: = " + var1 + " " + var2 + " " + var3)


def f_not(se, scope, params):
    var1 = params[0]
    var2 = params[1]

    if is_valid_variable_name(var2):
        if var1 == 'true':
            scope.vars[var2[1:]] = 'false'
        else:
            scope.vars[var2[1:]] = 'true'
    else:
        error_message(scope, "Invalid variable name! Line: ! " + var1 + " " + var2)


def f_greater(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            v1 = float(var1)
            v2 = float(var2)

            if v1 > v2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
        except ValueError:
            error_message(scope, "Values are not numbers! Line: > " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: > " + var1 + " " + var2 + " " + var3)


def f_greaterequal(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            v1 = float(var1)
            v2 = float(var2)

            if v1 >= v2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
        except ValueError:
            error_message(scope, "Values are not numbers! Line: >= " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: >= " + var1 + " " + var2 + " " + var3)


def f_less(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            v1 = float(var1)
            v2 = float(var2)

            if v1 < v2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
        except ValueError:
            error_message(scope, "Values are not numbers! Line: < " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: < " + var1 + " " + var2 + " " + var3)


def f_lessequal(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            v1 = float(var1)
            v2 = float(var2)

            if v1 <= v2:
                scope.vars[var3[1:]] = 'true'
            else:
                scope.vars[var3[1:]] = 'false'
        except ValueError:
            error_message(scope, "Values are not numbers! Line: <= " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: <= " + var1 + " " + var2 + " " + var3)


def f_slength(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_valid_variable_name(var2):
        scope.vars[var2[1:]] = len(var1)


def f_add(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        try:
            scope.vars[var3[1:]] = str(float(var1) + float(var2))
        except ValueError:
            scope.vars[var3[1:]] = var1 + var2
    else:
        error_message(scope, "Invalid variable name! Line: + " + var1 + " " + var2 + " " + var3)


def f_sub(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        try:
            scope.vars[var3[1:]] = str(float(var1) - float(var2))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: - " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: - " + var1 + " " + var2 + " " + var3)


def f_mul(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        try:
            scope.vars[var3[1:]] = str(float(var1) * float(var2))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: * " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: * " + var1 + " " + var2 + " " + var3)


def f_div(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        try:
            scope.vars[var3[1:]] = str(float(var1) / float(var2))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: / " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: / " + var1 + " " + var2 + " " + var3)


def f_mod(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    if is_valid_variable_name(var3):
        try:
            scope.vars[var3[1:]] = str(float(var1) % float(var2))
        except ValueError:
            error_message(scope, "Variables are not numbers! Line: % " + var1 + " " + var2 + " " + var3)
    else:
        error_message(scope, "Invalid variable name! Line: % " + var1 + " " + var2 + " " + var3)


def f_rnd(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_valid_variable_name(var2):
        try:
            scope.vars[var2[1:]] = str(round(float(var1)))
        except ValueError:
            error_message(scope, "Variable is not number! Line: round " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variable name! Line: round " + var1 + " " + var2)


def f_flr(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_valid_variable_name(var2):
        try:
            scope.vars[var2[1:]] = str(floor(float(var1)))
        except ValueError:
            error_message(scope, "Variable is not number! Line: floor " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variable name! Line: floor " + var1 + " " + var2)


def f_ceil(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    if is_valid_variable_name(var2):
        try:
            scope.vars[var2[1:]] = str(ceil(float(var1)))
        except ValueError:
            error_message(scope, "Variable is not number! Line: ceil " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variable name! Line: ceil " + var1 + " " + var2)


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

    scope.functions[var_name] = CustomFunctionDefinition(se, var_name, param_count, params[2] == 'true', params[3])


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

    se.global_fcns[var_name] = CustomFunctionDefinition(se, var_name, param_count, params[2] == 'true', params[3])


def f_floattoint(se, scope, params):
    var1 = params[0]
    var2 = params[1]

    if is_valid_variable_name(var2):
        try:
            var1 = int(float(var1))
            scope.vars[var2[1:]] = str(var1)
        except ValueError:
            error_message(scope, "Value not able to convert to int! Line: floattoint " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variable name! Line: floattoint " + var1 + " " + var2)


def f_charat(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]

    if is_valid_variable_name(var3):
        try:
            var2 = int(var2)
            if var2 >= len(var1) or var2 < 0:
                error_message(scope, "Index invalid! Line: charat " + params[0] + " " + params[1])
            else:
                scope.vars[var3[1:]] = var1[var2]
        except ValueError:
            error_message(scope, "Index invalid! Line: charat " + params[0] + " " + params[1])
    else:
        error_message(scope, "Invalid variable name! Line: charat " + var1 + " " + var2)


def f_chartoint(se, scope, params):
    var1 = params[0]
    var2 = params[1]

    if is_valid_variable_name(var2):
        try:
            var1 = ord(var1)
            scope.vars[var2[1:]] = str(var1)
        except ValueError:
            error_message(scope, "Value not able to convert to int! Line: chartoint " + var1 + " " + var2)
    else:
        error_message(scope, "Invalid variable name! Line: chartoint " + var1 + " " + var2)


def f_substr(se, scope, params):
    var1 = params[0]
    var2 = params[1]
    var3 = params[2]
    var4 = params[3]

    if is_valid_variable_name(var4):
        try:
            scope.vars[var4[1:]] = var1[int(var2):int(var3)]
        except ValueError:
            error_message(scope, "Invalid indexes! Line: substr " + var1 + " " + var2 + " " + var3 + " " + var4)
    else:
        error_message(scope, "Invalid variable name! Line: substr " + var1 + " " + var2 + " " + var3 + " " + var4)


def f_exec(se, scope, params):
    var1 = params[0]
    var2 = params[1]

    if var1 == 'true':
        se.execute_script(ScriptingScope(), var2)
    else:
        se.execute_script(scope, var2)


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

    def __init__(self, env, fcn_name, param_count, new_scope, tgt_fcn):
        """
        @type env: ScriptingEnvironment
        @type fcn_name: str
        @type param_count: int
        @type new_scope: bool
        @type tgt_fcn: function (ScriptingEnvironment, list[str])
        """

        self.env = env
        self.fcn_name = fcn_name
        self.param_count = param_count
        self.new_scope = new_scope
        self.tgt_fcn = tgt_fcn

    def invoke(self, scope, params):
        """
        Triggers this function with the given parameters
        @type scope: ScriptingScope
        @type params: list[str]
        @rtype: None
        """
        if self.new_scope:
            self.tgt_fcn(self.env, ScriptingScope(), params)
        else:
            self.tgt_fcn(self.env, scope, params)


class CustomFunctionDefinition(FunctionDefinition):

    def invoke(self, scope, params):
        if self.new_scope:
            fcn_scope = ScriptingScope()
            for i in range(self.param_count):
                fcn_scope.vars['PARAM' + str(i)] = params[i]
            self.env.execute_script(fcn_scope, self.tgt_fcn.replace('\\"', '"'))
        else:
            for i in range(self.param_count):
                scope.vars['PARAM' + str(i)] = params[i]
            self.env.execute_script(scope, self.tgt_fcn.replace('\\"', '"'))
