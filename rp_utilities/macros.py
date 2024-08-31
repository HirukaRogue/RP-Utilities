import traceback
import random
import lark
import re
from lark import Lark, Transformer
import discord
from .pagination import Paginator
from .miscellaneous import is_link
from .miscellaneous import mathematic
from .miscellaneous import roll


##################
### ROLL MACRO ###
##################
async def exeroll(args, res_type):
    print(f"{res_type = }")

    if "#" in args:
        parts = args.split("#")

        if parts[0].isnumeric:
            num_str = roll(parts[1], res_type, int(parts[0]))
        else:
            num_str = "Invalid Argument"

    else:
        num_str = roll(args, res_type)
    return num_str


##################
### MATH MACRO ###
##################
async def exemath(args: str, res_type: str):
    result = mathematic(args)
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
    key_cont.5: "{" (use_var | execute | command2 | formater) "}"
    finput: "[" (("(" content ")" ("," "(" content ")")*) | content) "]"
    
    formater: (black | italic | underline | spoiler | line)+ " " string

    black: "b"
    italic: "i"
    underline: "u"
    spoiler: "s"
    line: "l"

    string: CHAR_CHAIN+
    args: EXPRESSIONS+
    
    EXPRESSIONS: CHAR_EXP+
    CHAR_EXP: "0".."9"
                | "d" | "f" 
                | "k" | "p" | "rr" | "ro" | "ra" | "e" | "mi" | "ma"
                | "h" | "l" | "&gt;" | "<" | "=" | "!" | "%"
                | "+" | "-" | "*" | "/" | "."
                | "(" | ")" | "#"
    CHAR_CHAIN: CHAR+
    CHAR: /[^(){}\[\] ]/
    number: SIGNED_NUMBER 
    ws: WS

    %import common.INT
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
""",
    start="chain_command",
)


def repl(match):
    piv = match.group()
    piv = piv.replace("\\0", " ")
    return piv


async def conversor(macro: str):
    ### This part is making use of space easier to handle, so there is no need to always type \0
    ### for handling wise
    pattern = r"\[(.*?)\]"
    pivots = re.findall(pattern, macro)
    for i in pivots:
        piv = i
        macro = macro.replace(f"[{i}]", "[mask]")
        piv = piv.replace(" ", "\\0")
        piv = re.sub("\\{ *(.+?) *\\}", repl, piv)
        macro = macro.replace("[mask]", f"[{piv}]")

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
            traceback.print_tb(error.__traceback__)
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

        rl = cmd

        if len(cmd) > 1:
            opt = cmd[1]
            rl = cmd[0]
        else:
            opt = "all"
            rl = cmd

        rl = await trim(rl)

        result = await exeroll(args=rl, res_type=opt)
        return [result]

    async def echo(self, cmd):
        ec = cmd[0]
        prompt = await exeecho(ec)
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

        command = await database.quick_search_macro(prefix=scmd, id=self.macrocache["author_id"])

        if command is None:
            command = await database.quick_search_macro(prefix=scmd, id=self.macrocache["guild_id"])

        guild = macrocache["bot"].get_guild(int(self.macrocache["guild_id"]))
        member = guild.get_member(int(self.macrocache["author_id"]))

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
                print(f"{args = }")
                grammar_compilation = macro_grammar.parse(args)
            except (lark.UnexpectedCharacters, lark.LarkError) as error:
                indicator = error.get_context(args)
                # print(error.__traceback__)
                traceback.print_tb(error.__traceback__)
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
