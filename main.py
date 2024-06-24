import json
import os
import sys
import time

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

import player_util
from image_reader import ImageReader

config = {}
image_reader: ImageReader


# display desktop notification with given title and text
def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


# takes in a list of usernames (IGNs), gives notifications and prints a threat analysis
def do_threat_analysis(ign_list, key, ignored_usernames=None):
    if ignored_usernames is None:
        ignored_usernames = []
    print("\n\nFound " + str(len(ign_list)) + " players: ")
    for username in ign_list:
        print(username, end=", ")
    print("\n")

    # open file with all previous players
    with open(str(os.path.dirname(os.path.abspath(__file__))) + '/prev_players.json') as f:
        data = f.read()

    # reconstructing the data as a dictionary
    prev_players = json.loads(data)

    players = {}
    nicks = []
    sweats = []
    threats = []

    for ign in ign_list:
        # ignore usernames in ignored list
        if ign.lower() in (player_name.lower() for player_name in ignored_usernames):
            continue

        try:
            threat_analysis = player_util.get_player_info(ign, key)
        except Exception as err:

            if err.args[0] == "Nick or Not Player":
                prev_players[ign] = "Nick or Not Player"
                nicks.append(ign)
                continue

            elif err.args[0] == "Repeat":
                if ign in prev_players:
                    if prev_players[ign] == "Nick or Not Player":
                        nicks.append(ign)
                    else:
                        players[ign] = prev_players[ign]
                else:
                    print("Warning: Player " + ign + " currently on cooldown.")
                continue

            elif err.args[0] == "New Player":
                print(ign + " is a new player.")
                continue

            else:
                raise

        players[ign] = threat_analysis
        prev_players[ign] = threat_analysis

    # write back to the prev players file
    with open(str(os.path.dirname(os.path.abspath(__file__))) + '/prev_players.json', 'w') as players_file:
        players_file.write(json.dumps(prev_players))

    # sort the players by the number of final kills
    players = dict(sorted(players.items(), key=lambda x: x[1]["Finals"], reverse=True))

    threat_thresholds = {"Finals": 1000, "Beds": 1000, "FKDR": 2.0,
                         "Winstreak": 4, "Max Winstreak": 5, "Bridge Rating": 2}
    sweat_thresholds = {"Finals": 10000, "Beds": 10000, "FKDR": 5.0,
                        "Winstreak": 10, "Max Winstreak": 10, "Bridge Rating": 7}

    for player in players:
        sweat = False
        threat = False
        for stat in players[player]:
            if players[player][stat] > sweat_thresholds[stat]:
                sweat = True
            elif players[player][stat] > threat_thresholds[stat]:
                threat = True

        if sweat:
            sweats.append(player)
        elif threat:
            threats.append(player)

    notification = ""

    if len(nicks) > 0:
        print("\nNicks: ", end="")
        print(*nicks, sep=", ")

        notification += "Nicks: " + str(len(nicks)) + " "
    if len(sweats) > 0:
        print("\nSweats: ", end="")
        print(*sweats, sep=", ")

        notification += "Sweats: " + str(len(sweats)) + " "
    if len(threats) > 0:
        print("\nThreats: ", end="")
        print(*threats, sep=", ")

        notification += "Threats: " + str(len(threats)) + " "

    for player in players:
        print(player)
        print("    ", end="")
        for key in players[player]:
            print("%s: %6s" % (key, str(players[player][key])), end="   ")
        print()

    if len(notification) == 0:
        notify("Done!", "No threats here")
    else:
        notify("Done!", notification)


# takes in a string representing the path to a directory and returns the path to the most recent file in that directory
def get_latest_image(directory):
    latest_image = None
    latest_time = 0

    # Iterate through all the files in the directory
    for file in os.listdir(directory):
        if file == ".DS_Store":
            continue

        # Get the modified time of the file
        creation_time = os.path.getmtime(os.path.join(directory, file))
        # If the modified time is more recent than the current latest time, update the latest time and file
        if creation_time > latest_time:
            latest_time = creation_time
            latest_image = file

    return directory + latest_image


class Handler(FileSystemEventHandler):

    def on_any_event(self, event: FileSystemEvent) -> None:
        # Ignore non creation events
        if not event.event_type == 'created':
            return

        # Get image
        recent_image = get_latest_image(config["screenshots_directory"])

        # Wait until image is fully loaded
        limit = 20
        while True:
            try:
                username_list = image_reader.get_text_from_image(recent_image)
                break
            except OSError:
                if limit <= 0:
                    print("Screenshot image failed to load")
                    return
                else:
                    limit = limit - 1

        do_threat_analysis(username_list, config["api_key"], config["ignored_usernames"])


def main():
    # Ensure confiig file exists, read the config file into memory
    global config
    try:
        with open(str(os.path.dirname(os.path.abspath(__file__))) + '/config.json') as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        print("config.json file not found. Create a config.json file to continue")

    # Check for new API Key passed in as system argument
    if len(sys.argv) == 2:
        config["api_key"] = sys.argv[1]
        # Write new key back to the config file
        with open(str(os.path.dirname(os.path.abspath(__file__))) + '/config.json', 'w') as players_file:
            players_file.write(json.dumps(config))

    # Check to ensure API Key works
    try:
        player_util.api_request("t", config["api_key"])
    except Exception as err:
        if err.args[0] == "Invalid API key":
            print("Invalid API Key, generate a new key with 'https://developer.hypixel.net/dashboard'."
                  "Then, either add the key to config.json or use the key as an argument when running the program.")
            return
        elif "Unexpected exception" in err.args[0]:
            print(err.args[0])
            return
    print("API Key Validated")

    # Initialize ImageReader
    global image_reader
    image_reader = ImageReader()

    # Start file system watcher
    observer = Observer()
    event_handler = Handler()
    try:
        observer.schedule(event_handler, config["screenshots_directory"])
        observer.start()
    except Exception as err:
        if err.args[0] == "Invalid API key":
            print("Invalid API Key, generate a new key with 'https://developer.hypixel.net/dashboard'."
                  "Then, either add the key to config.json or use the key as an argument when running the program.")
        else:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
