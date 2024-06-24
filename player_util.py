import requests


# Take in player ign and key and gets player's data from the API
def api_request(player_name, key):
    raw_data = requests.get(
        url="https://api.hypixel.net/player",
        params={
            "key": key,
            "name": player_name
        }
    ).json()

    # check for error conditions
    if raw_data is None:
        # API Problem
        raise Exception("Unexpected API Issue")

    if not raw_data["success"]:

        if raw_data["cause"] == "Invalid API key":
            raise Exception("Invalid API key")
        elif raw_data["cause"] == "You have already looked up this name recently":
            raise Exception("Repeat")
        else:
            raise Exception("Unexpected exception: " + raw_data["cause"])

    if raw_data['player'] is None:
        # This means the player is unrecognized, either nicked or not a player
        raise Exception("Nick or Not Player")

    # set raw data to just the bedwars data
    try:
        raw_data = raw_data["player"]["stats"]["Bedwars"]
    except KeyError:
        raise Exception("New Player")

    return raw_data


# Takes in player's name and API key, returns dictionary wih the player's stats
def get_player_info(player_name, key):
    player_json = api_request(player_name, key)

    # Initialize player_data with finals, beds, and winstreak data
    player_data = {"Finals": player_json["final_kills_bedwars"] if "final_kills_bedwars" in player_json else 0,
                   "Beds": player_json["beds_broken_bedwars"] if "beds_broken_bedwars" in player_json else 0,
                   "Winstreak": player_json["winstreak"] if "winstreak" in player_json else 0}

    # Get fkdr data
    if "final_deaths_bedwars" not in player_json or player_json["final_deaths_bedwars"] == 0:
        player_data["FKDR"] = 0
    else:
        player_data["FKDR"] = round(10 * player_data["Finals"] / player_json["final_deaths_bedwars"]) / 10

    # Get max gamemode winstreak data
    gamemodes = ["four_four_", "eight_two_", "eight_one_", "four_three_"]
    max_winstreak = 0
    for mode in gamemodes:
        max_winstreak = max(max_winstreak, player_json[mode + "winstreak"] if mode + "winstreak" in player_json else 0)
    player_data["Max Winstreak"] = max_winstreak

    try:
        raw_data = player_json["practice"]["records"]
    except KeyError:
        player_data["Bridge Rating"] = 0
        return player_data

    # Get bridging score data
    thresholds = {"bridging_distance_30:elevation_NONE:angle_STRAIGHT:": 9500,
                  "bridging_distance_30:elevation_NONE:angle_DIAGONAL:": 8500,
                  "bridging_distance_30:elevation_SLIGHT:angle_STRAIGHT:": 13000,
                  "bridging_distance_30:elevation_SLIGHT:angle_DIAGONAL:": 12000,
                  "bridging_distance_30:elevation_STAIRCASE:angle_STRAIGHT:": 17000,
                  "bridging_distance_30:elevation_STAIRCASE:angle_DIAGONAL:": 20000}
    score = 0

    for bridging_type in thresholds:
        time = raw_data[bridging_type] if bridging_type in raw_data else 400000

        if time < thresholds[bridging_type]:
            score += 1

    player_data["Bridge Rating"] = score

    return player_data
