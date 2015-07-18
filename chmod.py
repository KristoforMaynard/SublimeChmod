import os
import subprocess
import stat

import sublime
import sublime_plugin

def get_stat(filename):
    """ returns an integer """
    return os.stat(filename).st_mode

def chmod(fname, current_perms_int, desired_perms):
    who_bits = {'u': stat.S_IRWXU, 'g': stat.S_IRWXG, 'o': stat.S_IRWXO,
                'a': stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
               }
    perm_bits = {
                 'r': stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH,
                 'w': stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH,
                 'x': stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                }

    if desired_perms == "":
        return None

    if desired_perms.find(",") >= 0:
        sublime.message_dialog("Can only handle one change at a time")
        return None

    try:
        mode = (current_perms_int & ~who_bits['a']) | int(desired_perms, base=8)
    except ValueError:
        mode = current_perms_int

        if desired_perms.find("+") >= 0:
            who, perm = desired_perms.split("+")
            if len(who) == 0:
                who = 'a'
            for iwho in who:
                for iperm in perm:
                    mode |= who_bits[iwho] & perm_bits[iperm]
        elif desired_perms.find("-") >= 0:
            who, perm = desired_perms.split("-")
            if len(who) == 0:
                who = 'a'
            for iwho in who:
                for iperm in perm:
                    mode &= ~(who_bits[iwho] & perm_bits[iperm])
        elif desired_perms.find("=") >= 0:
            who, perm = desired_perms.split("=")
            if len(who) == 0:
                who = 'a'
            for iwho in who:
                mode &= ~who_bits[iwho]  # clear this user
                for iperm in perm:
                    mode |= who_bits[iwho] & perm_bits[iperm]
        else:
            sublime.message_dialog("Unable to understand the "
                                   "desired permissions.")
            return None

    try:
        # print("chmod {0}: {1} -> {2}".format(fname, oct(current_perms_int), 
        #                                      oct(mode)))
        os.chmod(fname, mode)
    except Exception as e:
        sublime.message_dialog("Unable to chmod: {0}".format(e.message))
    return None

def action(fname, perms=""):
    if fname == None:
        sublime.message_dialog("No file selected.")
    else:
        current_perms_int = get_stat(fname)
        current_perms = oct(current_perms_int & 0o777).lstrip("0o")

        def done(desired_perms):
            try:
                cmd = "chmod {0} {1}".format(desired_perms, fname)
                subprocess.check_output(cmd.split())
            except Exception:  # pylint: disable=broad-except
                chmod(fname, current_perms_int, desired_perms)

        if perms == "":
            sublime.active_window().show_input_panel(
                "chmod {0} from {1} to:".format(fname, current_perms),
                "", done, None, None)
        else:
            done(perms)

class SublemakeChmodCommand(sublime_plugin.TextCommand):
    def run(self, edit, perms=""):
        fname = self.view.file_name()
        if fname == None:
            sublime.message_dialog("You need to save this buffer first!")
        else:        
            action(fname, perms=perms)


class SublemakeSidebarChmodCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[None], perms=""):
        fname = paths[0]
        action(fname, perms=perms)


##
## EOF
##
