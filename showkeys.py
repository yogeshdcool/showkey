import re, subprocess


def read_file(path):
    with open(path) as file:
        content = file.read()
    return content


def dwm():
    output = ""
    for match in re.finditer(
        r"\s*{\s*(.*?),\s*((?:XK|XF).*?),\s*(.*?),\s*(.*)\s*},",
        read_file("examples/config.def.h"),
    ):
        mod = (
            match.group(1)
            .replace("|", "+")
            .replace("MODKEY", "Mod")
            .replace("Mod1Mask", "Alt")
            .replace("ControlMask", "Ctrl")
            .replace("ShiftMask", "Shift")
        )
        key = match.group(2).replace("XK_", "")
        func = match.group(3)
        cmd = match.group(4)
        # binding = mod + "+" + key
        if mod == "0":
            binding = key
        else:
            binding = mod + "+" + key

        output = output + mod + "<>" + key + "<>" + func + "<>" + cmd + "\n"

    for match in re.finditer(
        r"\s*{\s*(Clk.*?),\s*(.*?),\s*(Button.*?),\s*(.*?),\s*(.*?)\s*},",
        read_file("examples/config.def.h"),
    ):
        output = (
            output
            + match.group(1)
            + "<>"
            + match.group(2)
            + "<>"
            + match.group(3)
            + "<>"
            + match.group(4)
            + match.group(5)
            + "\n"
        )
    return output


def show(wm, launcher):
    subprocess.run(f"echo '{wm()}' | column -s '<>' -t | {launcher}", shell=True)


# count = dwm().count("\n")
show(dwm, "rofi -dmenu -p ShowKeys")
# show(dwm, "dmenu -l 15 -p ShowKeys")
# print(dwm(), end="")
