import re
import subprocess
import argparse


def get_envs() -> str:
    """Get the name of available environment using ps command

    Returns:
        str: name(s) of available envs
    """
    ps_out = subprocess.run(
        r"ps -A | grep -Ei '\bdwm\b|\bi3\b|\bsxhkd\b'",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout
    if "sxhkd" in ps_out:
        return "sxhkd"
    elif "dwm" in ps_out:
        return "dwm"
    elif "i3" in ps_out:
        return "i3"
    else:
        return False


parser = argparse.ArgumentParser(
    description="Displays keybindings", prog="Showkeys", epilog=";)"
)
parser.add_argument(
    "-l", "--launcher", default="rofi -dmenu -p ShowKeys", help="Launcher to use"
)
parser.add_argument("env", default=[get_envs()], help="WM/DE/App to use", nargs="*")
args = parser.parse_args()


def read_file(path) -> str:
    """Returns the content if the given file

    Args:
        path (str): Path to the file

    Returns:
        str: Content of the file
    """
    with open(path) as file:
        content = file.read()
    return content


def dwm():
    keys_output = ""
    mouse_output = ""
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
        if mod == "0":
            binding = key
        else:
            binding = mod + "+" + key

        keys_output = keys_output + binding + "<>" + func + "<>" + cmd + "\n"

    for match in re.finditer(
        r"\s*{\s*(Clk.*?),\s*(.*?),\s*(Button.*?),\s*(.*?),\s*(.*?)\s*},",
        read_file("examples/config.def.h"),
    ):
        mouse_output = (
            match.group(1)
            + "<>"
            + match.group(2)
            .replace("|", "+")
            .replace("MODKEY", "Mod")
            .replace("Mod1Mask", "Alt")
            .replace("ControlMask", "Ctrl")
            .replace("ShiftMask", "Shift")
            + "<>"
            + match.group(3)
            + "<>"
            + match.group(4)
            + match.group(5)
            + "\n"
        )
    return keys_output


def i3():
    output = ""
    for match in re.finditer(
        r"(?:bindsym|bindcode)\s*(?:--release)?\s*([\w+$]*)\s*(?:exec)?\s*(?:--no-startup-id)?\s*(.*)",
        read_file("examples/config"),
    ):
        output = (
            output
            + match.group(1).replace("$mod", "mod")
            + "<>"
            + match.group(2)
            + "\n"
        )
    return output


def sxhkd():
    output = ""
    for match in re.finditer(
        r"(^[^#\s].*)\n\s*(.*)", read_file("examples/sxhkdrc"), re.MULTILINE
    ):
        output = output + match.group(1) + "<>" + match.group(2) + "\n"
    return output


bspwm = sxhkd


def main():
    rofi_modes = ""
    for env in args.env:
        func = eval(env + "()")
        bindings = subprocess.run(
            f"echo '{func}' | column -s '<>' -t",
            shell=True,
            text=True,
            capture_output=True,
        ).stdout
        rofi_modes = rofi_modes + f"{env}:\"printf\" '{bindings}',"
    print(rofi_modes)
    subprocess.run(
        f'rofi -modes "{rofi_modes}" -show {args.env[0]} -sidebar-mode', shell=True
    )


if __name__ == "__main__":
    main()
