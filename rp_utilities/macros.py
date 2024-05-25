import traceback
import random
import lark
from sympy import sympify
import re
from lark import Lark, Transformer
import discord
from .pagination import Paginator
from .miscellaneous import is_link


##################
### ROLL MACRO ###
##################
async def exeroll(args, res_type: str):
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
                        roll_result = await sub_roll(x)
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
                sub_total = await calculate(indice, store)
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
                    roll_result = await sub_roll(x)
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
            total = await calculate(indice, store)

        # resp_total will be the output of the roll
        resp_total = f"```\n{resp_sub}\n```\n:game_die: **__Total__** = {total}"

        return (
            resp_total
            if res_type == "only_string"
            else total if res_type == "only_result" else [resp_total, total]
        )
    else:
        return "ERROR!"


async def calculate(indice, store):
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


async def sub_roll(inp):
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
async def exemath(args: str, res_type: str):
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
async def exeselect(args):
    number = len(args) - 1
    selected = args[random.randint(0, number)]
    return selected


##################
### ECHO MACRO ###
##################
async def exeecho(args):
    print(f"{args = }")
    if len(args) == 1:
        y = await trim(args)
        y = y.replace("\\n", "\n")
        y = y.replace("\\0", " ")
        print(f"{y = }")
        pages = discord.Embed(description=y)
    else:
        chapters = list()
        for i in args:
            y = await trim(i)
            print(f"{y = }")
            y = y.replace("\\n", "\n")
            y = y.replace("\\0", " ")
            embed = discord.Embed(description=y)
            chapters.append(embed)
        pages = Paginator(chapters)
    return pages


###############
### TRIMMER ###
###############
async def trim(trimed):
    if isinstance(trimed, list):
        print(f"{trimed = }")
        if len(trimed) > 1:
            piv = ""
            for z in trimed:
                if z == trimed[-1] and isinstance(z, discord.Embed):
                    piv = piv + str(z.description)
                elif isinstance(z, discord.Embed):
                    piv = piv + f"{z.description}"
                elif z == trimed[-1] and isinstance(z, list):
                    piv = piv + f"{z[1]}"
                elif z == trimed[-1]:
                    piv = piv + str(z)
                elif isinstance(z, list):
                    piv = piv + f"{z[1]}"
                else:
                    piv = piv + f"{z}"
            trimed = piv
            return trimed
        return await trim(trimed[0])
    else:
        if isinstance(trimed, discord.Embed):
            return trimed.description
        else:
            return trimed


#################
### EXE IMAGE ###
#################
async def exe_image(image):
    output = discord.Embed()
    output.set_image(url=image)

    return output


macro_grammar = Lark(
    r"""
    chain_command: command (ws command)*
    command.2: (fif | command3)
    command2.2: (fif2 | command4)
    command3.2: (echo | command4)
    command4.2: (variable | roll | math | select | image)

    variable: "$" command

    fif.3: command3 " " "!if" " " comparator " " felse
    fif2.3: command4 " " "!if" " " comparator " " felse2
    felse.3: "!else" " " command
    felse2.3: "!else" " " command2

    roll.4:  "!roll" " " content2 ("," showtype)?
    math.4: "!math" " " content2 ("," showtype)?
    echo.4: "!echo" " " finput
    select.4: "!select" " " finput
    image.4: "!image" " " string
    execute.4: "!exe" " " sub_command
    
    listing.4: "!list" " " finput
    showtype.4: OPTIONS
    OPTIONS: "0" | "1" | "2"

    comparator.3: command2 " " comparator_indx
    comparator_indx: major | minor | equalmajor | equalminor | different | equal | inlist
    major: ">" (content | number | command2 | execute | listing)
    minor: "<" (content | number | command2 | execute | listing)
    equalmajor: ">=" (content | number | command2 | execute | listing)
    equalminor: "<=" (content | number | command2 | execute | listing)
    different: "!=" (content | number | command2 | execute | listing)
    equal: "==" (content | number | command2 | execute | listing)
    inlist: "in" (content | number | command2 | execute | listing)

    use_var.2: "&" INT
    sub_command: string
    content.5: string? (key_cont string?)*
    content2.5: args? (key_cont args?)*
    key_cont.5: "{" (use_var | execute | command2 | formater | ascii_character) "}"
    finput: "[" (("(" content ")" ("," "(" content ")")*) | content) "]"
    
    formater: (black | italic | underline | spoiler | line)+ " " string

    black: "b"
    italic: "i"
    underline: "u"
    spoiler: "s"
    line: "l"

    ascii_character: cidilha | crase | agudo | tio | circumflexo | position | degree | invert_inter | invert_exc
    position: a | o
    invert_inter: "invert ?"
    invert_exc: "invert !"
    
    cidilha: "cid"
    degree: "deg"
    
    a: "pos-a"
    o: "pos-o"

    crase: "`" " " LETRA_PRIM | LETRA_SEC
    agudo: "´" " " LETRA_PRIM | LETRA_SEC
    tio: "~" " " (LETRA_PRIM | LETRA_ESPECIAL)
    circumflexo: "^" " " LETRA_PRIM | LETRA_SEC

    LETRA_PRIM: "a" | "o"
    LETRA_SEC: "e" | "i" | "u"
    LETRA_ESPECIAL: "n"
    
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
           | "<" | "=" | ">" | "?" | "@" | "^" | "_" | "`" | "|" | "~" | "¨" | "¢" | "¬" | "§"
    number: SIGNED_NUMBER 
    ws: WS

    %import common.INT
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
""",
    start="chain_command",
)


async def conversor(macro: str):
    ### This part is ASCII transformation
    # special characters
    macro = macro.replace("ç", r"{ cid }")

    # punctuation
    macro = macro.replace("à", r"{ ` a }")
    macro = macro.replace("è", r"{ ` e }")
    macro = macro.replace("ì", r"{ ` i }")
    macro = macro.replace("ò", r"{ ` o }")
    macro = macro.replace("ù", r"{ ` u }")

    macro = macro.replace("á", r"{ ´ a }")
    macro = macro.replace("é", r"{ ´ e }")
    macro = macro.replace("í", r"{ ´ i }")
    macro = macro.replace("ó", r"{ ´ o }")
    macro = macro.replace("ú", r"{ ´ u }")

    macro = macro.replace("ã", r"{ ~ a }")
    macro = macro.replace("ñ", r"{ ~ n }")
    macro = macro.replace("õ", r"{ ~ o }")

    macro = macro.replace("â", r"{ ^ a }")
    macro = macro.replace("ê", r"{ ^ e }")
    macro = macro.replace("î", r"{ ^ i }")
    macro = macro.replace("ô", r"{ ^ o }")
    macro = macro.replace("û", r"{ ^ u }")

    # positional symbols
    macro = macro.replace("ª", r"{ pos-a }")
    macro = macro.replace("º", r"{ pos-o }")
    macro = macro.replace("°", r"{ deg }")

    # inverted punctuations
    macro = macro.replace("¡", r"{ invert ! }")
    macro = macro.replace("¿", r"{ invert ? }")

    return macro


class AsyncTransformer(Transformer):
    """Async variant of a Lark Transformer.  For calling coroutines."""

    __visit_tokens__ = True  # For backwards compatibility

    def __init__(self, macrocache: dict, visit_tokens: bool = True) -> None:
        self.__visit_tokens__ = visit_tokens
        self.macrocache = macrocache

    async def _call_userfunc(self, tree, new_children=None):
        # Assumes tree is already transformed
        children = new_children if new_children is not None else tree.children
        try:
            f = getattr(self, tree.data)
        except AttributeError:
            return await self.__default__(tree.data, children, tree.meta)
        else:
            try:
                wrapper = getattr(f, "visit_wrapper", None)
                if wrapper is not None:
                    return await f.visit_wrapper(f, tree.data, children, tree.meta)
                else:
                    return await f(children)
            except lark.exceptions.GrammarError:
                raise
            except Exception as e:
                raise lark.exceptions.VisitError(tree.data, tree, e)

    async def _call_userfunc_token(self, token):
        try:
            f = getattr(self, token.type)
        except AttributeError:
            return await self.__default_token__(token)
        else:
            try:
                print("Calling userfunc token.")
                return await f(token)
            except lark.exceptions.GrammarError:
                raise
            except Exception as e:
                raise lark.exceptions.VisitError(token.type, token, e)

    async def _transform_children(self, children):
        for c in children:
            if isinstance(c, lark.Tree):
                res = await self._transform_tree(c)
            elif self.__visit_tokens__ and isinstance(c, lark.Token):
                res = await self._call_userfunc_token(c)
            else:
                res = c

            if res is not lark.visitors.Discard:
                yield res

    async def _transform_tree(self, tree):
        children = []
        async for c in self._transform_children(tree.children):
            children.append(c)
        return await self._call_userfunc(tree, children)

    async def transform(self, tree: lark.Tree) -> lark.Tree:
        "Transform the given tree, and return the final result"
        return await self._transform_tree(tree)

    async def __default__(self, data, children, meta):
        """Default function that is called if there is no attribute matching ``data``

        Can be overridden. Defaults to creating a new copy of the tree node (i.e. ``return Tree(data, children, meta)``)
        """
        return lark.Tree(data, children, meta)

    async def __default_token__(self, token):
        """Default function that is called if there is no attribute matching ``token.type``

        Can be overridden. Defaults to returning the token as-is.
        """
        return token


class Compiler(AsyncTransformer):
    async def chain_command(self, macro):
        try:
            chain_cmd = list()
            for i in macro:
                if i != " ":
                    chain_cmd.append(i)
            return chain_cmd
        except (lark.UnexpectedCharacters, lark.LarkError) as error:
            indicator = error.get_context(macro, len(macro))
            print(error.__traceback__)
            raise CompilationIncompatibility(indicator)

    async def command4(self, cmd):
        (cmd4,) = cmd
        return cmd4

    async def command3(self, cmd):
        (cmd3,) = cmd
        return cmd3

    async def command2(self, cmd):
        (cmd2,) = cmd
        return cmd2

    async def command(self, cmd):
        (cmd,) = cmd
        return cmd

    async def execute(self, cmd):
        print(cmd)
        return cmd

    async def math(self, cmd):

        if len(cmd) > 1:
            opt = cmd[1]
            m = cmd[0]
        else:
            opt = "all"
            m = cmd

        m = await trim(m)
        result = await exemath(args=m, res_type=opt)
        return result

    async def select(self, cmd):
        sl = cmd[0]
        result = await exeselect(sl)
        return result

    async def roll(self, cmd):
        print(f"{cmd = }")

        if len(cmd) > 1:
            opt = cmd[1]
            rl = cmd[0]
        else:
            opt = "all"
            rl = cmd

        print(f"{rl = }")

        rl = await trim(rl)

        print(f"{rl = }")

        result = await exeroll(args=rl, res_type=opt)
        return [result]

    async def echo(self, cmd):
        ec = cmd[0]
        prompt = await exeecho(ec)
        print(f"{prompt = }")
        return [prompt]

    async def fif(self, cmd):
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

    async def felse(self, cmd):
        result = cmd
        return [result]

    async def fif2(self, cmd):
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

    async def felse2(self, cmd):
        result = cmd
        return [result]

    async def comparator(self, cmd):
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

    async def comparator_indx(self, cmd):
        (cindx,) = cmd
        try:
            cindx[1] = float(cindx[1])
            return cindx
        except:
            return cindx

    async def major(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">", index]

    async def minor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["<", index]

    async def equalmajor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">=", index]

    async def equalminor(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return [">=", index]

    async def equal(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["==", index]

    async def different(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["!=", index]

    async def inlist(self, cmd):
        index = cmd
        while True:
            index = index[0]
            if isinstance(index, str):
                break

        return ["in", index]

    async def variable(self, cmd):
        print("Registering variable")
        var = cmd
        while True:
            var = var[0]
            if len(var) > 1:
                piv = ""
                for i in var:
                    if i == var[-1]:
                        if isinstance(i, list):
                            if len[i] > 1:
                                piv = piv + str(i[1])
                            else:
                                piv = piv + str(i[0])
                        else:
                            piv = piv + str(i)
                    else:
                        if isinstance(i, list):
                            if len(i) > 1:
                                piv = piv + f" {str(i[1])}"
                            else:
                                piv = piv + f" {str(i[0])}"
                        else:
                            piv = piv + f" {str(i)}"
                    var = piv
            if isinstance(var, str):
                break
        await macrocache["database"].cache_register(id=macrocache["author_id"], var=var)
        return var

    async def use_var(self, cmd):
        print("Gathering Variable")
        var_pos = int(cmd[0])
        variables = await macrocache["database"].get_cache(id=macrocache["author_id"])
        use_var = variables[var_pos]
        return use_var

    async def sub_command(self, cmd):
        acesscmd = cmd[0]
        if not acesscmd.startswith("+>") and not acesscmd.startswith("->"):
            raise BadStartingException(acesscmd)

        scmd = acesscmd
        database = self.macrocache["database"]

        print(f"{scmd = }")

        command = await database.quick_search_macro(prefix=scmd, id=self.macrocache["author_id"])

        if command is None:
            command = await database.quick_search_macro(prefix=scmd, id=self.macrocache["guild_id"])

        print(f"{macrocache['guild_id'] = }")
        print(f"{macrocache['author_id'] = }")

        guild = macrocache["bot"].get_guild(int(self.macrocache["guild_id"]))
        member = guild.get_member(int(self.macrocache["author_id"]))

        print(f"{guild = }")
        print(f"{member = }")

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
                result = await Compiler(self.macrocache).transform(
                    macro_grammar.parse(command["cmd"])
                )
                return result

    async def content(self, cmd):
        cnt = cmd
        return [cnt]

    async def content2(self, cmd):
        cnt = cmd
        return [cnt]

    async def expression(self, cmd):
        (exp,) = cmd
        return exp

    async def key_cont(self, cmd):
        print(f"{cmd = }")
        kcont = cmd
        if isinstance(kcont, list):
            while True:
                print(f"{kcont = }")
                if not isinstance(kcont, list):
                    break
                if len(kcont) > 1:
                    break
                kcont = kcont[0]
        if isinstance(kcont, float):
            return float(kcont)
        else:
            return kcont

    async def finput(self, cmd):
        (inp,) = [cmd]
        return inp

    async def string(self, cmd):
        command_string = str()
        for i in range(0, len(cmd)):
            if i == 0:
                command_string += cmd[i]
            else:
                command_string += " " + cmd[i]
        return command_string

    async def args(self, cmd):
        math_arguments = cmd
        return math_arguments

    async def image(self, cmd):
        acess = await trim(cmd)
        if is_link(acess):
            image = acess
            op = await exe_image(image)

            return [op]
        else:
            raise NotURLException()

    async def showtype(self, cmd):
        num = int(cmd[0])
        if num == 0:
            return "all"
        elif num == 1:
            return "only_string"
        elif num == 2:
            return "only_result"

    async def formater(self, cmd):
        text = cmd[-1]
        frmtr = cmd
        frmtr.pop(-1)

        if "b" in frmtr:
            text = f"**{text}**"
        if "i" in frmtr:
            text = f"*{text}*"
        if "u" in frmtr:
            text = f"__{text}__"
        if "l" in frmtr:
            text = f"~~{text}~~"
        if "s" in frmtr:
            text = f"||{text}||"

        return text

    async def black(self, cmd):
        return "b"

    async def italic(self, cmd):
        return "i"

    async def underline(self, cmd):
        return "u"

    async def spoiler(self, cmd):
        return "s"

    async def line(self, cmd):
        return "l"

    async def ws(self, cmd):
        return None

    async def ascii_character(self, cmd):
        print(cmd)
        return cmd

    async def cidilha(self, cmd):
        return "ç"

    async def degree(self, cmd):
        return "°"

    async def position(self, cmd):
        return cmd

    async def a(self, cmd):
        return "ª"

    async def o(self, cmd):
        return "º"

    async def crase(self, cmd):
        if "a" in cmd:
            return "à"
        if "e" in cmd:
            return "è"
        if "i" in cmd:
            return "ì"
        if "o" in cmd:
            return "ò"
        if "u" in cmd:
            return "ù"

    async def agudo(self, cmd):
        print(f"agudo = {cmd}")
        if "a" in cmd:
            return "á"
        if "e" in cmd:
            return "é"
        if "i" in cmd:
            return "í"
        if "o" in cmd:
            return "ó"
        if "u" in cmd:
            return "ú"

    async def tio(self, cmd):
        if "a" in cmd:
            return "ã"
        if "o" in cmd:
            return "õ"
        if "n" in cmd:
            return "ñ"

    async def circumflexo(self, cmd):
        if "a" in cmd:
            return "â"
        if "e" in cmd:
            return "ê"
        if "i" in cmd:
            return "î"
        if "o" in cmd:
            return "ô"
        if "u" in cmd:
            return "û"

    async def invert_inter(self, cmd):
        return "¿"

    async def invert_exc(self, cmd):
        return "¡"


##########################
###   MACRO EXECUTER   ###
##########################
class Macro:
    async def exemac(self, args, database, guild_id, author_id, bot, starter):
        macrocache["command"] = args
        macrocache["database"] = database
        macrocache["guild_id"] = guild_id
        macrocache["author_id"] = author_id
        macrocache["bot"] = bot
        macrocache["start with ->"] = starter

        try:
            print(f"{args = }")
            try:
                args = await conversor(args)
                grammar_compilation = macro_grammar.parse(args)
            except (lark.UnexpectedCharacters, lark.LarkError) as error:
                indicator = error.get_context(args)
                print(error.__traceback__)
                raise InvalidCharacter(indicator)

            cmd = await Compiler(macrocache).transform(grammar_compilation)

            # await macrocache["database"].clear_cache(id=macrocache["author_id"])

            return cmd
        except Exception as e:
            print(e)
            return (e,)


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
        string = macrocache["command"]
        string.replace(f"!exe {macro}", f"!exe ***{macro}***")
        self.message = (
            string
            + "server private macros can only be used on another server private macros or you don't have admin permissions to use the macro, please update the macro to public or protected"
        )

        super().__init__(self.message)


### Non-Existant Macro Exception ###
class NonExistantMacro(Exception):
    def __init__(self, macro) -> None:
        string = macrocache["command"]
        string.replace(f"!exe {macro}", f"!exe ***{macro}***")
        self.message = string + "\nThi macro don't exist"

        super().__init__(self.message)


### Bad Starting Macro Exception ###
class BadStartingException(Exception):
    def __init__(self, cmd: str) -> None:
        string = macrocache["command"]
        string.replace(f"!exe {cmd}", f"!exe ***{cmd}***")
        self.message = string + "\nThe macro shall start with +> or ->"

        super().__init__(self.message)


class InvalidCharacter(Exception):
    def __init__(self, string: str) -> None:
        highlight = string.split("\n")
        result = ""

        limit = False
        for i, _ in enumerate(highlight[0]):
            if not limit:
                if highlight[1][i] != " ":
                    pivot = f"***{highlight[0][i]}***"
                    result = result + pivot
                    limit = True
                else:
                    result = result + highlight[0][i]
            else:
                result = result + highlight[0][i]

        self.message = (
            result + "\nThis character is not compatible with compiler or you mistyped something"
        )

        super().__init__(self.message)


class CompilationIncompatibility(Exception):
    def __init__(self, string) -> None:
        highlight = string.split("\n")
        result = ""

        limit = False
        for i, _ in enumerate(highlight[0]):
            if not limit:
                if highlight[1][i] != " ":
                    pivot = f"***{highlight[0][i]}***"
                    result = result + pivot
                    limit = True
                else:
                    result = result + highlight[0][i]
            else:
                result = result + highlight[0][i]

        self.message = result + "\nThis argument is invalid"

        super().__init__(self.message)


class NotURLException(Exception):
    def __init__(self) -> None:
        self.message = "Image URL invalid, paste the image url or try another image url"

        super().__init__(self.message)
