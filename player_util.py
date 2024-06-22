import requests


# take in player ign and key and returns a dictionary with just useful information about them
def get_info(player_name, key):
    player_data = {}

    raw_data = requests.get(
        url="https://api.hypixel.net/player",
        params={
            "key": key,
            "name": player_name
        }
    ).json()

    # check for error conditions
    if raw_data is None:
        # Player not recognized
        raise Exception("No data")

    if not raw_data["success"]:
        # This means the player's data was accessed too recently and cannot be accessed again
        raise Exception("Repeat")

    if raw_data['player'] == "None" or raw_data['player'] is None:
        # This means the player is a nicked player
        raise Exception("Nick")

    # set raw data to just the bedwars data
    try:
        raw_data = raw_data["player"]["stats"]["Bedwars"]
    except KeyError:
        raise Exception("New Player")

    # Get finals data
    player_data["Finals"] = raw_data["final_kills_bedwars"] if "final_kills_bedwars" in raw_data else 0

    # Get beds data
    player_data["Beds"] = raw_data["beds_broken_bedwars"] if "beds_broken_bedwars" in raw_data else 0

    # Get fkdr data
    if "final_deaths_bedwars" not in raw_data or raw_data["final_deaths_bedwars"] == 0:
        player_data["FKDR"] = 0
    else:
        player_data["FKDR"] = round(10 * player_data["Finals"] / raw_data["final_deaths_bedwars"]) / 10

    # Get winstreak data
    player_data["Winstreak"] = raw_data["winstreak"] if "winstreak" in raw_data else 0

    # Get max gamemode winstreak data
    gamemodes = ["four_four_", "eight_two_", "eight_one_", "four_three_"]
    max_winstreak = 0
    for mode in gamemodes:
        max_winstreak = max(max_winstreak, raw_data[mode + "winstreak"] if mode + "winstreak" in raw_data else 0)
    player_data["Max Winstreak"] = max_winstreak

    try:
        raw_data = raw_data["practice"]["records"]
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
