#!/usr/bin/env python3

import psutil
import os
import urllib.request
import tarfile
import subprocess
from halo import Halo
import signal

the_spinner='dots4'

global_ourpath  = None
global_cwd      = None

# kill existing processes
def func_killext():
    for proc in psutil.process_iter():
        if "steamcmd" in proc.name():
            os.kill(proc.pid, signal.SIGKILL)
        if "murse" in proc.name():
            os.kill(proc.pid, signal.SIGKILL)


def get_userpath():
    ourpath = input("Where would you like to install Open Fortress, relative to the current directory?\n")
    cwd = os.getcwd()

    global global_ourpath
    global_ourpath = ourpath

    global global_cwd
    global_cwd = cwd


def func_mkdir(path):
    mkdir_spinner = Halo(text=f'Making directory {path}...', spinner=the_spinner)
    mkdir_spinner.start()

    try:
        os.mkdir(path)
    except FileExistsError:
        print("Directory already exists...")
        quit()
    except FileNotFoundError:
        print("Parent directory doesn't exist...?")
        quit()
    except:
        print("idk man")
        quit()

    mkdir_spinner.succeed(f"Made directory {path}")


def func_cd(path):
    cd_spinner = Halo(text=f'Changing directory to {path}...', spinner=the_spinner)
    cd_spinner.start()

    try:
        os.chdir(path)
    except PermissionError:
        cd_spinner.fail("No permissions to this directory!!")
        quit()
    except FileNotFoundError:
        cd_spinner.fail("Couldn't find directory to change to...")
        quit()
    except NotADirectoryError:
        cd_spinner.fail("Tried to cd to a file...?")
        quit()

    cd_spinner.succeed(f"Changed directory to {path}")

# in 
def getSteamcmd():
    dl_steamcmd_spinner = Halo(text='Downloading SteamCMD...', spinner=the_spinner)
    dl_steamcmd_spinner.start()

    steamcmd_linux_url="https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"

    try:
        urllib.request.urlretrieve(steamcmd_linux_url, "steamcmd.tgz")
    except:
        spinner.fail("Failed to download SteamCMD!")
        quit()
    dl_steamcmd_spinner.succeed("Downloaded SteamCMD.")

    try:
        steamcmd_tgz = tarfile.open('steamcmd.tgz')
        steamcmd_tgz.extractall('./')
        steamcmd_tgz.close()
    except:
        dl_steamcmd_spinner.fail("Failed while extracting SteamCMD!")
        quit()
    dl_steamcmd_spinner.succeed("Extracted SteamCMD.")
    dl_steamcmd_spinner.stop()


def getMurse():
    dl_murse_spinner = Halo(text='Downloading Murse...', spinner=the_spinner)
    dl_murse_spinner.start()

    murse_v="v0.2.1"
    murse_url=f"https://git.sr.ht/~welt/murse/refs/download/{murse_v}/murse-{murse_v}-linux-amd64.tar.gz"

    try:
        urllib.request.urlretrieve(murse_url, "murse.tgz")
    except:
        dl_murse_spinner.fail("Failed to download Murse!")
        quit()
    dl_murse_spinner.succeed("Downloaded Murse.")

    try:
        murse_tgz = tarfile.open('murse.tgz')
        murse_tgz.extractall('./')
        murse_tgz.close()
    except:
        dl_murse_spinner.fail("Failed extracting Murse.")
        quit()
    dl_murse_spinner.succeed("Extracted Murse.")
    dl_murse_spinner.stop()


def initSteamcmd():
    steamcmd_init = "./steamcmd.sh +quit"

    steamcmd_spinner = Halo(text='Updating SteamCMD...', spinner=the_spinner)
    steamcmd_spinner.start()

    # these seem to be autoclosed
    out = open("./steamcmd_init.out", "w")
    err = open("./steamcmd_init.err", "w")

    try:
        subprocess.run(steamcmd_init.split(), stdout=out, stderr=err)
    except:
        steamcmd_spinner.fail("SteamCMD failed while updating!")
        quit()

    steamcmd_spinner.succeed("SteamCMD finished updating.")

    fullupdate_file = open("./fullupdate.txt", "w")
    fullupdate_file.write("""
@ShutdownOnFailedCommand 1
@NoPromptForPassword 1
// tf2
force_install_dir ./tf2d
login anonymous
app_update 232250
logoff
// sdk2013
force_install_dir ./sdk
login anonymous
app_update 244310
logoff
quit
""")
    fullupdate_file.close()
    steamcmd_spinner.succeed("SteamCMD finished initializing.")
    steamcmd_spinner.stop()


global_steamcmd_proces  = None
global_murse_proces     = None

def dosteamcmd_fullupdate():
    steamcmd_fullupdate = "./steamcmd.sh +runscript fullupdate.txt"
    steamcmd_verify     = "./steamcmd.sh +runscript fullupdate.txt"

    out = open("./steamcmd_full.out", "w")
    err = open("./steamcmd_full.err", "w")

    fullupdate_sh = open("./steamcmd_fullupdate.sh", "w")
    fullupdate_sh.write(f"""
#!/bin/bash
{steamcmd_fullupdate}
""")
    fullupdate_sh.close()

    steamcmd_process = subprocess.Popen(steamcmd_fullupdate.split(), stdout=out, stderr=err)

    global global_steamcmd_process
    global_steamcmd_process = steamcmd_process


def domurse_fullupdate():
    murse_threads = 2
    murse_upgrade = f"./murse upgrade -G sdk/open_fortress -c {murse_threads}"

    out = open("./murse.out", "w")
    err = open("./murse.err", "w")


    murse_fullupgrade_sh = open("./murse_fullupdate.sh", "w")
    murse_fullupgrade_sh.write(f"""
#!/bin/bash
{murse_upgrade}
""")
    murse_fullupgrade_sh.close()

    murse_process = subprocess.Popen(murse_upgrade.split(), stdout=out, stderr=err)

    global global_murse_proces
    global_murse_proces = murse_process


def dosteamcmd_block():
    steamcmd_out, steamcmd_err = global_steamcmd_process.communicate()
    ret = global_steamcmd_process.returncode
    if ret != 0:
        bothspinners.fail(f"Something went wrong with SteamCMD! Exit code was {ret}.")
        quit()


def domurse_block():
    murse_out, murse_err = global_murse_proces.communicate()
    ret = global_murse_proces.returncode
    if ret != 0:
        bothspinners.fail(f"Something went wrong with Murse! Exit code was {ret}.")
        quit()


def getGameFiles():
    bothspinners = Halo(text='SteamCMD and Murse are downloading files! Be patient...', spinner=the_spinner)
    bothspinners.start()
    
    # these run independently of each other
    dosteamcmd_fullupdate()
    domurse_fullupdate()
    
    # these do not block independently of each other
    dosteamcmd_block()
    domurse_block()
    
    bothspinners.succeed("Done downloading game files.")
    bothspinners.stop()


def lnBins():
    sdk_bin = [
        "datacache_srv.so",             "datacache.so",
        "dedicated_srv.so",             "dedicated.so",
        "engine_srv.so",                "engine.so",
        "materialsystem_srv.so",        "materialsystem.so",
        "replay_srv.so",                "replay.so",
        "scenefilecache_srv.so",        "scenefilecache.so",
        "shaderapiempty_srv.so",        "shaderapiempty.so",
        "soundemittersystem_srv.so",    "soundemittersystem.so",
        "studiorender_srv.so",          "studiorender.so",
        "vphysics_srv.so",              "vphysics.so"
    ]

    # Yes this is backwards from the ones above
    of_bin = [
        "server.so",                    "server_srv.so",
    ]

    out = open("./ln.out", "w")
    err = open("./ln.err", "w")

    out = open("./ln.out", "a")
    err = open("./ln.err", "a")

    # sdk/bin
    func_cd("./sdk/bin")

    ln_spinner = Halo(text='Linking SDK binaries...', spinner=the_spinner)
    ln_spinner.start()

    for i in range(len(sdk_bin)):
        # odd
        if i % 2 == 1:
            lncmd = f"ln -s {sdk_bin[i-1]} {sdk_bin[i]}"
            try:
                subprocess.run(lncmd.split(), stdout=out, stderr=err)
            except:
                ln_spinner.fail("Failed linking SDK binaries!")
                quit()

    ln_spinner.succeed("Linked SDK binaries.")
    ln_spinner.stop()

    func_cd("../open_fortress/bin")

    ln_spinner = Halo(text='Linking Open Fortress binaries...', spinner=the_spinner)
    ln_spinner.start()

    for i in range(len(of_bin)):
        # odd
        if i % 2 == 1:
            lncmd = f"ln -s {of_bin[i-1]} {of_bin[i]}"
            try:
                subprocess.run(lncmd.split(), stdout=out, stderr=err)
            except:
                ln_spinner.fail("Failed linking Open Fortress binaries!")
                quit()

    ln_spinner.succeed("Linked Open Fortress binaries.")
    ln_spinner.stop()

    # install_dir root
    func_cd("../../../")


def doGameinfo():
    gameinfo_spinner = Halo(text='Autogenerating gameinfo.txt...', spinner=the_spinner)
    gameinfo_spinner.start()

    func_cd("./sdk/open_fortress")
    gameinfo_chunk_1 = """
"GameInfo"
{
    game                        "Open Fortress"
    title                       ""
    title2                      ""  
    gamelogo                    "1"
    developer                   "https://openfortress.fun"
    developer_url               "https://openfortress.fun"
    manual                      ""

    type                        "multiplayer_only"
    hasportals                  "0"     // gameui.dll
    hashdcontent                "0"     // gameui.dll
    nomodels                    "0"     // gameui.dll
    nohimodel                   "0"     // gameui.dll
    nocrosshair                 "0"     // gameui.dll
    advcrosshair                "1"     // gameui.dll
    nodifficulty                "1"     // gameui.dll
    supportsvr                  "0"     // engine.dll + gameui.dll
    bots                        "0"     // gameui.dll
    nodegraph                   "1"     // engine.dll
    perfwizard                  "0"     // unused
    SupportsDX8                 "0"     // unused
    SupportsDX9                 "1"     // unused
    SupportsDX10                "0"     // unused
    SupportsDX11                "0"     // unused
    SupportsXbox                "0"     // unused
    SupportsXbox360             "0"     // unused
    SupportsXboxOne             "0"     // unused
    SupportsPS3                 "0"     // unused
    SupportsPS4                 "0"     // unused
    icon                        "resource/game"
    GameData                    "ofd_fic2.fgd"
    InstancePath                "maps/instances/"
    
    hidden_maps
    {
        "test_speakers"         1
        "test_hardware"         1
        "background01"          1
        "background02"          1
        "background03"          1
        "background04"          1
        "background05"          1
        "background06"          1
        "background07"          1
        "background08"          1
        "background09"          1
        "background12"          1
        "background15"          1
        "ep1_c17_00"            1
        "ep1_c17_00a"           1
        "ep1_c17_01"            1
        "ep1_c17_01a"           1
        "ep1_c17_02"            1
        "ep1_c17_02a"           1
        "ep1_c17_02b"           1
        "ep1_c17_05"            1
        "ep1_c17_06"            1
        "ep1_citadel_00"        1
        "ep1_citadel_00_demo"   1
        "ep1_citadel_01"        1
        "ep1_citadel_02"        1
        "ep1_citadel_02b"       1
        "ep1_citadel_03"        1
        "ep1_citadel_04"        1
        "ep1_background01"      1
        "ep1_background01a"     1
        "ep1_background02"      1
        "ep2_outland_01"        1
        "ep2_outland_01a"       1
        "ep2_outland_02"        1
        "ep2_outland_03"        1
        "ep2_outland_04"        1
        "ep2_outland_05"        1
        "ep2_outland_06"        1
        "ep2_outland_06a"       1
        "ep2_outland_07"        1
        "ep2_outland_08"        1
        "ep2_outland_09"        1
        "ep2_outland_10"        1
        "ep2_outland_10a"       1
        "ep2_outland_11"        1
        "ep2_outland_11a"       1
        "ep2_outland_11b"       1
        "ep2_outland_12"        1
        "ep2_outland_12a"       1
        "ep2_background01"      1
        "ep2_background02"      1
        "ep2_background02a"     1
        "ep2_background03"      1
        "credits"               1
        "vst_lostcoast"         1
        "test"                  1
        "sdk_vehicles"          1
    }

    FileSystem
    {
        SteamAppId              243750
        
        SearchPaths
        {
            game+mod            |gameinfo_path|custom/*
            game+game_write+mod+mod_write+default_write_path |gameinfo_path|.
            gamebin             |gameinfo_path|bin
            
            // The lines below until the BREAK comment are responsible for the game resources to work properly
            // in Hammer and other Source tools. The default setup assumes that you have everything (Steam, TF2,
            // Source SDK and OF) in the same drive letter/partition. If you have a different storage configuration,
            // feel free to modify the paths below between quotes
"""
    gameinfo_chunk_2 = f"""
            // Autogenerated by https://github.com/sapphonie/open-fortress-srcds-autosetup
            game                "{global_cwd}/{global_ourpath}/tf2d/tf/tf2_misc.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/tf/tf2_sound_misc.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/tf/tf2_sound_vo_english.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/tf/tf2_textures.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/tf"
            
            game                "{global_cwd}/{global_ourpath}/tf2d/hl2/hl2_textures.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/hl2/hl2_sound_vo_english.vpk"
            game                "{global_cwd}/{global_ourpath}/tf2d/hl2/hl2_sound_misc.vpk"
"""

    gameinfo_chunk_3 = """
            // The hl2 folder here is from Source SDK Base 2013 Multiplayer.
            game                "|all_source_engine_paths|hl2/hl2_misc.vpk"
            game                "|all_source_engine_paths|hl2"
            // ========== BREAK ==========
            
            platform            |all_source_engine_paths|platform/platform_misc.vpk
            platform            |all_source_engine_paths|platform
            
            game+download       |gameinfo_path|download
        }
    }
}"""
    gameinfo = open("./gameinfo.txt", "w")
    gameinfo.write(f"{gameinfo_chunk_1}{gameinfo_chunk_2}{gameinfo_chunk_3}")
    gameinfo.close()
    func_cd("../../")

    gameinfo_spinner.succeed(f"Autogenerated gameinfo.txt!")
    gameinfo_spinner.stop()


def makeSh():
    makesh_spinner = Halo(text='Creating startup shell script...', spinner=the_spinner)
    makesh_spinner.start()

    of_sh = open("./sdk/of.sh", "w")
    of_sh.write(f"""
#!/bin/bash
./{global_cwd}/{global_ourpath}/sdk/srcds_run -console -game open_fortress -port 27015 +ip "0.0.0.0" -nohltv \
+maxplayers 24 +map dm_crossfire +sv_cheats 0 \
-autoupdate -steam_dir {global_cwd}/{global_ourpath}/ -steamcmd_script {global_cwd}/{global_ourpath}/fullupdate.txt
""")
    of_sh.close()

    makesh_spinner.succeed(f"Created startup script! Do `bash {global_cwd}/{global_ourpath}/sdk/of.sh` to start your server.")
    makesh_spinner.stop()





func_killext()
get_userpath()
func_mkdir(global_ourpath)
func_cd(global_ourpath)
getSteamcmd()
getMurse()
initSteamcmd()
getGameFiles()
lnBins()
doGameinfo()
makeSh()
