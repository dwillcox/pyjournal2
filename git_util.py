from __future__ import print_function

import os
import re
import sys

import entry_util
import master_util
import shell_util

#=============================================================================
# journal-specific routines
#=============================================================================

def init(nickname, master_path, working_path, defs):

    # check the working path to make sure it is absolute, not relative
    working_path = os.path.normpath(working_path)
    if not working_path.startswith("/"):
        working_path = os.path.abspath(working_path)

    # make sure that a journal with this nickname doesn't already exist
    if nickname in defs.keys():
        sys.exit("ERROR: nickname already exists")

    # we are create the directory beneath master_path/, so make sure that
    # exists
    master_path = os.path.normpath(master_path)
    if not master_path.startswith("/"):
        master_path = os.path.abspath(master_path)
    
    if not os.path.isdir(master_path):
        try: os.mkdir(master_path)
        except:
            sys.exit("ERROR: you need to specify an existing path in which to create the journal repo")

    # create the bare git repo
    git_master = "{}/journal-{}.git".format(master_path, nickname)
    try: os.mkdir(git_master)
    except:
        sys.exit("ERROR: unable to create a directory in {}".format(master_path))

    os.chdir(git_master)
    stdout, stderr, rc = shell_util.run("git init --bare")


    # create the local working copy
    try: os.chdir(working_path)
    except:
        sys.exit("ERROR: unable to change to {}".format(working_path))

    stdout, stderr, rc = shell_util.run("git clone " + git_master)


    # create the initial directory structure
    working_journal = "{}/journal-{}".format(working_path, nickname)

    try: os.mkdir(working_journal + "/entries/")
    except:
        sys.exit("ERROR: unable to create initial directory structure")


    # create (or add to) the .pyjournalrc file
    try: f = open(defs["param_file"], "a+")
    except:
        sys.exit("ERROR: unable to open {} for appending".format(defs["param_file"]))

    f.write("[{}]\n".format(nickname))
    f.write("master_repo = {}\n".format(git_master))
    f.write("working_path = {}\n".format(working_path))
    f.write("\n")
    f.close()

    defs[nickname] = {}
    defs[nickname]["master_repo"] = git_master
    defs[nickname]["working_path"] = working_path

    # create an initial entry saying "journal created"
    images = []
    entry_util.entry(nickname, images, defs, string="journal created")


    # copy over the journal.tex
    try: f = open("{}/journal.tex".format(working_journal), "w")
    except:
        sys.exit("ERROR: unable to open {}/journal.tex".format(working_journal))

    for line in master_util.journal_master.split("\n"):
        f.write("{}\n".format(line.rstrip()))

    f.close()


    # add journal.tex to the repo and do a git push to make it synced
    os.chdir(working_journal)

    stdout, stderr, rc = shell_util.run("git add journal.tex")
    stdout, stderr, rc = shell_util.run("git commit -m 'initial journal.tex file' journal.tex")
    stdout, stderr, rc = shell_util.run("git push origin master")


def connect(master_repo, working_path, defs):

    # get the nickname from the master repo name
    re_name = r"journal-(.*).git"
    a = re.search(re_name, master_repo)

    if not a == None:
        nickname = a.group(1)
    else:
        sys.exit("ERROR: the remote-git-repo should be of the form: ssh://machine/dir/journal-nickname.git")

    # make sure that a journal with this nickname doesn't already exist
    if nickname in defs.keys():
        sys.exit("ERROR: nickname already exists")

    # git clone the bare repo at master_repo into the working path
    try: os.chdir(working_path)
    except:
        sys.exit("ERROR: unable to switch to directory {}".format(working_path))

    stdout, stderr, rc = shell_util.run("git clone " + master_repo)
    if not rc == 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git clone")

    # create (or add to) the .pyjournalrc file
    try: f = open(defs["param_file"], "a+")
    except:
        sys.exit("ERROR: unable to open {} for appending".format(defs["param_file"]))

    f.write("[{}]\n".format(nickname))
    f.write("master_repo = {}\n".format(master_repo))
    f.write("working_path = {}\n".format(working_path))
    f.write("\n")
    f.close()



#=============================================================================
# general routines
#=============================================================================

def pull(defs, nickname=None):

    # switch to the working directory and pull from the master
    if not nickname == None:
        wd = "{}/journal-{}".format(defs[nickname]["working_path"], nickname)
    else:
        wd = "{}/todo_list".format(defs["working_path"])

    try: os.chdir(wd)
    except:
        sys.exit("ERROR: unable to switch to working directory: {}".format(wd))

    stdout, stderr, rc = shell_util.run("git pull")
    if not rc == 0:
        print(stdout, stderr)
        sys.exit("ERROR: something went wrong with the git pull")

    print(stdout)


def push(defs, nickname=None):

    # switch to the working directory and push to the master
    if not nickname == None:
        wd = "{}/journal-{}".format(defs[nickname]["working_path"], nickname)
    else:
        wd = "{}/todo_list".format(defs["working_path"])

    try: os.chdir(wd)
    except:
        sys.exit("ERROR: unable to switch to working directory: {}".format(wd))

    stdout, stderr, rc = shell_util.run("git push")
    if not rc == 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git push")

    print(stderr)