import traceback
import random
import lark
from sympy import sympify
import re
from lark import Lark, Transformer
import discord
from pagination import Paginator


##################
### ROLL MACRO ###
##################
def exeroll(args, res_type: str):
    # define boolean see if the code will work or not
    not_failure = True
    # start to make the roll
    # indice = index to store the operator variables, willl be
    # useful to know which operation the variable will do when calculating the total
    indice = list()
    # cont is the that will store which values will
    # interact with each other
    # function to detect the interaction through numbers and
    # which numbers will interact with the operator
    for indz in args:
        if indz == "+" or indz == "-" or indz == "*" or indz == "/" or indz == "(" or indz == ")":
            indice.append(indz)

    if "[" in args or "]" in args:
        not_failure = False

    # gather dice roll and numbers to calculate, sotring them into args_result, being args result the raw input
    # pattern = re.compile(r"^\[.+\]$")
    # args_sub_result = pattern.findall(args)
    # pattern = re.compile(r"^\(.+\)$")
    pattern = re.compile(r"[+\-*/]|(\[|\]|\(|\))")
    args_result = pattern.split(args)
    args_result = [elem for elem in args_result if elem not in [None, "(", ")", "[", "]"]]

    # total is the variable to store the total of the operation
    total = 0
    # testing the # occurance
    for y in args_result:
        if "#" in y:
            if y != args_result[0]:
                not_failure = False
                break

    if not_failure:
        resp_sub = ""
        # store will store the roll results as in an Array
        store = list()
        total = 0
        if "#" in args_result[0]:
            indice_pivot = indice
            # mark will mark how much occurances it will be for the multi-rollings,
            # mark will only store the first value
            mark = args_result[0].split("#")
            args_result[0] = mark[1]
            mark.pop(1)
            for z in range(0, int(mark[0])):
                # here will start the multi-rolling
                if z > 0:
                    resp_sub = resp_sub + f"{z + 1}#"
                else:
                    resp_sub = f"{z + 1}#"
                for indx, x in enumerate(args_result):
                    # this is the subroll of keach multiroll from a sequence of rolls
                    if indx > 0:
                        resp_sub = resp_sub + f"{indice[indx - 1]} {x}"
                    else:
                        resp_sub = resp_sub + f"{x}"
                    if x:
                        roll_result = sub_roll(x)
                        if not resp_sub:
                            resp_sub = f"{x}"
                            for roll_index in roll_result[0]:
                                resp_sub = resp_sub + f"({roll_index})"
                            resp_sub = resp_sub + f"[{roll_result[1]}]"
                        else:
                            for roll_index in roll_result[0]:
                                resp_sub = resp_sub + f"({roll_index})"
                            resp_sub = resp_sub + f"[{roll_result[1]}]"
                            store.append(roll_result[1])
                    else:
                        store.append(x)
                sub_total = calculate(indice, store)
                store.clear()
                total = total + sub_total
                resp_sub = resp_sub + f"<[{sub_total}]>" + "\n"
        else:
            # when there aren't a # it will initiate a single roll
            resp_sub = ""
            for indx, x in enumerate(args_result):
                # this will be a regular roll for each dice in the line, will be stored into store
                if indx > 0:
                    resp_sub = resp_sub + f"{indice[indx - 1]} {x}"
                if x:
                    roll_result = sub_roll(x)
                    if not resp_sub:
                        resp_sub = f"{x}"
                        for roll_index in roll_result[0]:
                            resp_sub = resp_sub + f"({roll_index})"
                        resp_sub = resp_sub + f"[{roll_result[1]}]"
                    else:
                        for roll_index in roll_result[0]:
                            resp_sub = resp_sub + f"({roll_index})"
                        resp_sub = resp_sub + f"[{roll_result[1]}]"
                    store.append(roll_result[1])
                else:
                    store.append(x)

            # the total will be cauculated by the calculate function
            total = calculate(indice, store)

        # resp_total will be the output of the roll
        resp_total = f"```\n{resp_sub}\n```\n:game_die: **__Total__** = {total}"

        return (
            resp_total
            if res_type == "only_string"
            else total if res_type == "only_result" else [resp_total, total]
        )
    else:
        return "ERROR!"


def calculate(indice, store):
    sub_total = 0
    expression = ""
    for i in range(0, len(store)):
        expression = expression + f"{store[i]}"
        if i < len(indice):
            if store[i] != "" and (indice[i] == "(" or indice[i] == "["):
                expression = expression + "*"
            if (indice[i] == ")" or indice[i] == "]") and store[i + 1] != "":
                expression = expression + "*"

            expression = expression + f"{indice[i]}"

    sub_total = sympify(expression)

    return sub_total


def sub_roll(inp):
    # This function will make thje rollings
    # result will be the rolls result, total will be the sum of the results
    # and meta will be results and total stored as metadata
    total = 0
    meta = list()
    result = list()

    if "d" in inp or "D" in inp:
        # if there is a d in inp it will detect as a dice
        pivot = inp.split("d")
        if pivot[1] == "f" or pivot[1] == "F":
            pivot2 = [random.randint(1, 6) for _ in range(int(pivot[0]))]
            for i in pivot2:
                if i == 1 or i == 2:
                    result.append("-")
                elif i == 5 or i == 6:
                    result.append("+")
                else:
                    result.append(0)
        elif pivot[1] == "c" or pivot[1] == "C":
            pivot2 = [random.randint(0, 1) for _ in range(int(pivot[0]))]
            for i in pivot2:
                if i == 0:
                    result.append("Heads")
                else:
                    result.append("Tails")
        else:
            result = [random.randint(1, int(pivot[1])) for _ in range(int(pivot[0]))]
    else:
        # if it's not a dice it will be a raw value
        total = int(inp)

    if result:
        for x in result:
            if x == "+":
                total = total + 1
            elif x == "-":
                total = total - 1
            elif x == "Heads" or x == "Tails":
                total = total
            else:
                total = total + x
    meta = [result, total]
    return meta


##################
### MATH MACRO ###
##################
def exemath(args: str, res_type: str):
    result = sympify(args)
    result_string = f"{args} = {result}"
    if res_type == "only_result":
        return result
    elif res_type == "only_string":
        return result_string
    elif res_type == "all":
        return [result_string, result]


####################
### SELECT MACRO ###
####################
def exeselect(args):
    number = len(args) - 1
    selected = args[random.randint(0, number)]
    return selected


##################
### ECHO MACRO ###
##################
def exeecho(args):
    if len(args) == 1:
        y = args
        if isinstance(y, list):
            while True:
                print(f"{y = }")
                if len(y) > 1:
                    piv = ""
                    for z in y:
                        piv = piv + (
                            z
                            if z == y[-1] and isinstance(z, str)
                            else (
                                f"{z[1]}"
                                if z == y[-1]
                                else f" {z}" if isinstance(z, str) else f" {z[1]}"
                            )
                        )
                    y = piv
                if isinstance(y, str) or isinstance(y, float):
                    break
                y = y[0]
        pages = discord.Embed(description=y)
    else:
        chapters = list()
        for i in args:
            y = i
            if isinstance(y, list):
                while True:
                    print(f"{y = }")
                    if len(y) > 1:
                        piv = ""
                        for z in y:
                            piv = piv + (
                                z
                                if z == y[-1] and isinstance(z, str)
                                else (
                                    f"{z[1]}"
                                    if z == y[-1]
                                    else f" {z}" if isinstance(z, str) else f" {z[1]}"
                                )
                            )
                        y = piv
                    if isinstance(y, str) or isinstance(y, float):
                        break
                    y = y[0]
            embed = discord.Embed(description=y)
            chapters.append(embed)
        pages = Paginator(chapters)
    return pages


macro_grammar = Lark(
    r"""
    chain_command: command (ws command)*
    command.2: (fif | command3)
    command2.2: (fif2 | command4)
    command3.2: (echo | command4)
    command4.2: (variable | roll | math | select)

    variable: "$" command

    fif.3: command3 " " "!if" " " comparator " " felse
    fif2.3: command4 " " "!if" " " comparator " " felse2
    felse.3: "!else" " " command
    felse2.3: "!else" " " command2

    roll.4:  "!roll" " " content2 ("," showtype)?
    math.4: "!math" " " content2 ("," showtype)?
    echo.4: "!echo" " " finput
    select.4: "!select" " " finput
    execute.4: "!exe" " " sub_command
    
    listing.4: "!list" " " finput
    showtype.4: OPTIONS
    OPTIONS: "0" | "1" | "2"

    comparator.3: command2 " " comparator_indx
    comparator_indx: major | minor | equalmajor | equalminor | different | equal | inlist
    major: ">" (content | number | command2 | sub_command | listing)
    minor: "<" (content | number | command2 | sub_command | listing)
    equalmajor: ">=" (content | number | command2 | sub_command | listing)
    equalminor: "<=" (content | number | command2 | sub_command | listing)
    different: "!=" (content | number | command2 | sub_command | listing)
    equal: "==" (content | number | command2 | sub_command | listing)
    inlist: "in" (content | number | command2 | sub_command | listing)

    use_var.2: "&" INT
    sub_command: string
    content.5: string? (key_cont string?)*
    content2.5: args? (key_cont args?)*
    key_cont.5: "{" (use_var | sub_command | command2) "}"
    finput: "[" (("(" content ")" ("," "(" content ")")*) | content) "]"

    string: CHAR_CHAIN+
    args: EXPRESSIONS+
    
    EXPRESSIONS: CHAR_EXP+
    CHAR_EXP: "0".."9"
                | "d" | "D" | "f" | "F" | "c" | "C" 
                | "+" | "-" | "*" | "/" | "."
                | "(" | ")" | "#"
    CHAR_CHAIN: CHAR+
    CHAR: "0".."9" | "a".."z" | "A".."Z" | SYMBOLS
    SYMBOLS: "!" | "#" | "$" | "%" | "&" | "\\" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" 
           | "<" | "=" | ">" | "?" | "@" | "^" | "_" | "`" | "|" | "~"
    number: SIGNED_NUMBER 
    ws: WS

    %import common.INT
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
""",
    start="chain_command",
)


class Compiler(Transformer):
    def chain_command(self, macro):
        chain_cmd = list()
        for i in macro:
            if i != " ":
                chain_cmd.append(i)
        return chain_cmd

    def command4(self, cmd):
        (cmd4,) = cmd
        return cmd4

    def command3(self, cmd):
        (cmd3,) = cmd
        return cmd3

    def command2(self, cmd):
        (cmd2,) = cmd
        return cmd2

    def command(self, cmd):
        (cmd,) = cmd
        return cmd

    def execute(self, cmd):
        return cmd

    def math(self, cmd):
        m = cmd

        if len(cmd) > 1:
            opt = cmd[1]
        else:
            opt = "all"

        while True:
            m = m[0]
            if isinstance(m, str):
                break
        result = exemath(args=m, res_type=opt)
        return result

    def select(self, cmd):
        sl = cmd[0]
        result = exeselect(sl)
        return result

    def roll(self, cmd):
        rl = cmd

        if len(cmd) > 1:
            opt = cmd[1]
        else:
            opt = "all"

        while True:
            rl = rl[0]
            if isinstance(rl, str):
                break
        result = exeroll(args=rl, res_type=opt)
        return [result]

    def echo(self, cmd):
        ec = cmd[0]
        prompt = exeecho(ec)
        return [prompt]

    def fif(self, cmd):
        cases = cmd
        if cases[1]:
            case = cases[0]
        else:
            case = cases[2]
        while True:
            if (
                isinstance(case, str)
                or isinstance(case, float)
                or isinstance(case, str)
                or len(case) > 1
            ):
                break
            case = case[0]
        return [case]

    def felse(self, cmd):
        result = cmd
        return [result]

    def fif2(self, cmd):
        cases = cmd
        if cases[1]:
            case = cases[0]
        else:
            case = cases[2]
        while True:
            if (
                isinstance(case, str)
                or isinstance(case, float)
                or isinstance(case, str)
                or len(case) > 1
            ):
                break
            case = case[0]
        return [case]

    def felse2(self, cmd):
        result = cmd
        return [result]

    def comparator(self, cmd):
        comp1 = cmd[0]
        comp2 = cmd[1]
        while True:
            if (
                isinstance(comp1, str)
                or isinstance(comp1, float)
                or isinstance(comp1, str)
                or len(comp1) > 1
            ):
                break
            comp1 = comp1[0]

        if comp2[0] == ">":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 > comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == "<":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 < comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == ">=":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 >= comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == "<=":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 <= comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == "==":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 == comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == "!=":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 != comp2[1]:
                return True
            else:
                return False

        elif comp2[0] == "in":
            if len(comp1) > 1 and not isinstance(comp1, str):
                comp1 = comp1[1]
            if comp1 == comp2[1]:
                return True
            else:
                return False

    def comparator_indx(self, cmd):
        (cindx,) = cmd
        try:
            cindx[1] = float(cindx[1])
            return cindx
        except:
            return cindx

    def major(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">", index]

    def minor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["<", index]

    def equalmajor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">=", index]

    def equalminor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">=", index]

    def equal(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["==", index]

    def different(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["!=", index]

    def inlist(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["in", index]

    def variable(self, cmd):
        var = cmd
        variables.append(var)
        return var

    def use_var(self, cmd):
        var_pos = int(cmd[0])
        use_var = variables[var_pos]
        return use_var

    def sub_command(self, cmd):
        if not cmd.startswith("+>") and not cmd.startswith("->"):
            raise BadStartingException()

        scmd = cmd
        database = macrocache["database"]

        command = database.quick_search_macro(prefix=scmd, id=macrocache["author_id"])
        if command == "ERROR":
            command = database.quick_search_macro(prefix=scmd, id=macrocache["guild_id"])

        guild = macrocache["bot"].get_guild(int(macrocache["guild_id"]))
        member = guild.get_member(int(macrocache["author_id"]))

        if command == "ERROR":
            raise NonExistantMacro(scmd)
        else:
            if (command["type"] == "server" and not member.guild_permissions.administrator) or (
                scmd.startswith("->") != macrocache["start with ->"]
                and command["attribute"] == "private"
                and command["prefix"].startswith("->")
            ):
                raise IllegalCommandParse(scmd)
            else:
                result = Compiler().transform(macro_grammar.parse(command["cmd"]))
                return result

    def content(self, cmd):
        cnt = cmd
        return [cnt]

    def content2(self, cmd):
        cnt = cmd
        return [cnt]

    def expression(self, cmd):
        (exp,) = cmd
        return exp

    def key_cont(self, cmd):
        kcont = cmd[0][0]
        return kcont

    def finput(self, cmd):
        (inp,) = [cmd]
        return inp

    def string(self, cmd):
        command_string = str()
        for i in range(0, len(cmd)):
            if i == 0:
                command_string += cmd[i]
            else:
                command_string += " " + cmd[i]
        return command_string

    def args(self, cmd):
        math_arguments = cmd
        return math_arguments

    def showtype(self, cmd):
        num = int(cmd[0])
        if num == 0:
            return "all"
        elif num == 1:
            return "only_string"
        elif num == 2:
            return "only_result"

    def ws(self, cmd):
        return None


#### Variables ####
variables = list()


##########################
###   MACRO EXECUTER   ###
##########################
async def exemac(args, database, guild_id, author_id, bot, starter):
    macrocache["database"] = database
    macrocache["guild_id"] = guild_id
    macrocache["author_id"] = author_id
    macrocache["bot"] = bot
    macrocache["start with ->"] = starter

    try:
        grammar_compilation = macro_grammar.parse(args)

        cmd = Compiler().transform(grammar_compilation)

        # variables.clear()

        return cmd
    except lark.LarkError:
        traceback.print_exc()
        return ("ERROR",)


#################
###   CACHE   ###
#################
macrocache = dict()


###############################
###############################
###############################


##### Macro error Handlers #####


### Private Macro Exception ###
class IllegalCommandParse(Exception):
    def __init__(self, macro) -> None:
        self.message = f"""server private macro can only be used on another server private macros or you don't have admin permissions to use the macro, please update the macro to public or protected
macro prefix: {macro}        
"""

        super().__init__(self.message)


### Non-Existant Macro Exception ###
class NonExistantMacro(Exception):
    def __init__(self, macro) -> None:
        self.message = f"The macro {macro} don't exist"

        super().__init__(self.message)


### Bad Starting Macro Exception ###
class BadStartingException(Exception):
    def __init__(self) -> None:
        self.message = "The macro shall start with +> or ->"

        super().__init__(self.message)
