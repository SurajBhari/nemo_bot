token = "ODI3NjExOTczNjgzMjQ5MTg0.YGdjtg.imdji648QR3bAkK_yatcW2xIT1I"
cogs = ["cogs.help", "cogs.Moderation"]
close = '<:stop:835558232420253736>'
unicode_emojis = []


class Personal_Server:
    colored_roles = [835624887346528266,
                     835624885673918505,
                     835624884465172530,
                     835624878538227753,
                     835624877003767818,
                     835624875506270228,
                     835624873991733329,
                     835624872595292160,
                     835624870930808913,
                     835624869437112410,
                     835624868040278037,
                     835624866593898596,
                     835624865201127454,
                     835624863796297768,
                     835624862201806907,
                     835624860965011538,
                     835624859580760104,
                     835624857974341683,
                     835624856652480542,
                     835624855146856548,
                     835624853259288597,
                     835624851850919947,
                     835624850134794362,
                     835624848755261461
                     ]
    guild_id = 835496578293825546


for i in range(10):  # generates unicode emojis [A,B,C,…]
    if i < 9:
        emoji = 'x\u20e3'.replace('x', str(i + 1))
    else:
        emoji = '\U0001f51f'

    unicode_emojis.append(emoji)
paginator_emojis = [
    "<:starting:835557611969314868>",
    "<:backward:835557609599795200>",
    "<:forward:835557609976365107>",
    "<:ending:835557609921970207>"
]
hidden_cogs = ["CommandErrorHandler", "main", "SQL", "Help", "Jishaku"]

lemonoji_mapping = {
    "a": ":r_b::l_b: \n"
         ":t_r_b::l_t_b: \n"
         ":head_b::end_b: ",
    "b": ":head_t::blank: \n"
         ":t_r_b::l_b: \n"
         ":t_r::l_t: ",
    "c": ":r_b::head_r: \n"
         ":t_b::blank: \n"
         ":t_r::end_r: ",
    "d": ":blank::head_t: \n"
         ":r_b::l_t_b: \n"
         ":t_r::l_t: ",
    "e": ":r_b::end_r: \n"
         ":t_r_b::head_r: \n"
         ":t_r::end_r: ",
    "f": ":r_b::head_r: \n"
         ":t_r_b::end_r: \n"
         ":end_b::blank: ",
    "g": ":r_b::l_b: \n"
         ":t_r::l_t_b: \n"
         ":head_l::l_t: ",
    "h": ":end_t::blank: \n"
         ":t_r_b::l_b: \n"
         ":end_b::head_b: ",
    "i": ":head_t: \n"
         ":t_b: \n"
         ":end_b: ",
    "j": ":blank::end_t: \n"
         ":head_t::t_b: \n"
         ":t_r::l_t: ",
    "k": "",
    "l": "",
    "m": "",
    "n": "",
    "o": "",
    "p": "",
    "q": "",
    "r": "",
    "s": "",
    "t": "",
    "u": "",
    "v": "",
    "w": "",
    "x": "",
    "y": "",
    "z": "",
    "0": "",
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
    "7": "",
    "8": "",
    "9": ""
}
