__license__ = """
NML is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

NML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with NML; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

# The following version determination code is a greatly simplified version
# of the mercurial repo code. The version is stored in nml/__version__.py
# get_numeric_version is used only for the purpose of packet creation,
# in all other cases use get_nml_version()

import subprocess, os

def get_child_output(cmd):
    """
    Run a child process, and collect the generated output.

    @param cmd: Command to execute.
    @type  cmd: C{list} of C{str}

    @return: Generated output of the command, split on whitespace.
    @rtype:  C{list} of C{str}
    """
    return subprocess.check_output(cmd, universal_newlines = True).split()


def get_hg_version():
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    version = ''
    if os.path.isdir(os.path.join(path,'.hg')):
        # we want to return to where we were. So save the old path
        try:
            version_list = get_child_output(['hg', '-R', path, 'id', '-n', '-t', '-i'])
        except OSError as e:
            print("Mercurial checkout found but cannot determine its version. Error({0}): {1}".format(e.errno, e.strerror))
            return version

        if version_list[1].endswith('+'):
            modified = 'M'
        else:
            modified = ''

        # Test whether we have a tag (=release version) and add it, if found
        if len(version_list) > 2 and version_list[2] != 'tip' and modified == '':
            # Tagged release
            version = version_list[2]
        else:
            # Branch or modified version
            hash = version_list[0].rstrip('+')

            # Get the date of the commit of the current NML version in days since January 1st 2000
            ctimes = get_child_output(["hg", "-R", path, "parent", "--template='{date|hgdate} {date|shortdate}\n'"])
            ctime = (int((ctimes[0].split("'"))[1]) - 946684800) // (60 * 60 * 24)
            cversion = str(ctime)

            # Combine the version string
            version = "v{}{}:{} from {}".format(cversion, modified, hash, ctimes[2].split("'", 1)[0])
    return version

def get_lib_versions():
    versions = {}
    #PIL
    try:
        from PIL import Image
        versions["PIL"] = Image.VERSION
    except ImportError:
        try:
            import Image
            versions["PIL"] = Image.VERSION
        except ImportError:
            versions["PIL"] = "Not found!"

    #PLY
    try:
        from ply import lex
        versions["PLY"] = lex.__version__
    except ImportError:
        versions["PLY"] = "Not found!"

    return versions

def get_nml_version():
    # first try whether we find an nml repository. Use that version, if available
    version = get_hg_version()
    if version:
        return version
    # no repository was found. Return the version which was saved upon built
    try:
        from nml import __version__
        version = __version__.version
    except ImportError:
        version = 'unknown'
    return version

def get_cli_version():
    #version string for usage in command line
    result = get_nml_version() + "\n"
    result += "Library versions encountered:\n"
    for lib, lib_ver in list(get_lib_versions().items()):
        result += lib + ": " + lib_ver + "\n"
    return result[0:-1] #strip trailing newline

def get_and_write_version():
    version = get_nml_version()
    if version:
        try:
            path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            f = open(os.path.join(path, "nml", "__version__.py"), "w")
            f.write('# this file is autogenerated by setup.py\n')
            f.write('version = "{}"\n'.format(version))
            f.close()
            return version.split()[0]
        except IOError:
            print("Version file NOT written")
