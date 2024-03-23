import discord
from discord import app_commands
from discord.ext import commands
import random
from sympy import sympify
import re


class RollCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roll.py is ready")

    @commands.command(aliases=["r", "diceroll", "dice_roll", "dice"], help="roll")
    async def roll(self, ctx, args: str):
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
            if indz in ("+", "-", "*", "/", "(", ")", "[", "]"):
                indice.append(indz)

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
                        resp_sub = resp_sub + f"{z+1}#"
                    else:
                        resp_sub = f"{z+1}#"
                    for indx, x in enumerate(args_result):
                        # this is the subroll of keach multiroll from a sequence of rolls
                        if indx > 0:
                            resp_sub = resp_sub + f"{indice[indx-1]} {x}"
                        else:
                            resp_sub = resp_sub + f"{x}"
                        if x:
                            roll_result = self.sub_roll(x)
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
                    sub_total = self.calculate(indice, store)
                    store.clear()
                    total = total + sub_total
                    resp_sub = resp_sub + f"<[{sub_total}]>" + "\n"
            else:
                # when there aren't a # it will initiate a single roll
                resp_sub = ""
                for indx, x in enumerate(args_result):
                    # this will be a regular roll for each dice in the line, will be stored into store
                    if indx > 0:
                        resp_sub = resp_sub + f"{indice[indx-1]} {x}"
                    if x:
                        roll_result = self.sub_roll(x)
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
                total = self.calculate(indice, store)

            # resp_total will be the output of the roll
            resp_total = f"```\n{resp_sub}\n```\n:game_die: **__Total__** = {total}"
            embed = discord.Embed(title="Roll Result", description=resp_total)

            await ctx.send(embed=embed)

        if not resp_total:
            resp_total = "Error! Invalid arguments"

            await ctx.send(resp_total)

    @app_commands.command(
        name="roll", description="roll 1 or more dices of any sides, can use DnD arguments"
    )
    @app_commands.describe(args="set the arguments of dice roll, like 1d20+5")
    async def roll_slash(self, interaction: discord.Interaction, args: str):
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
            if (
                indz == "+"
                or indz == "-"
                or indz == "*"
                or indz == "/"
                or indz == "("
                or indz == ")"
                or indz == "["
                or indz == "]"
            ):
                indice.append(indz)

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
                        resp_sub = resp_sub + f"{z+1}#"
                    else:
                        resp_sub = f"{z+1}#"
                    for indx, x in enumerate(args_result):
                        # this is the subroll of keach multiroll from a sequence of rolls
                        if indx > 0:
                            resp_sub = resp_sub + f"{indice[indx-1]} {x}"
                        else:
                            resp_sub = resp_sub + f"{x}"
                        if x:
                            roll_result = self.sub_roll(x)
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
                    sub_total = self.calculate(indice, store)
                    store.clear()
                    total = total + sub_total
                    resp_sub = resp_sub + f"<[{sub_total}]>" + "\n"
            else:
                # when there aren't a # it will initiate a single roll
                resp_sub = ""
                for indx, x in enumerate(args_result):
                    # this will be a regular roll for each dice in the line, will be stored into store
                    if indx > 0:
                        resp_sub = resp_sub + f"{indice[indx-1]} {x}"
                    if x:
                        roll_result = self.sub_roll(x)
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
                total = self.calculate(indice, store)

            # resp_total will be the output of the roll
            resp_total = f"```\n{resp_sub}\n```\n:game_die: **__Total__** = {total}"
            embed = discord.Embed(title="Roll Result", description=resp_total)

            await interaction.response.send_message(embed=embed)

    def calculate(self, indice, store):
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

    def sub_roll(self, inp):
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


async def setup(client):
    await client.add_cog(RollCog(client))
