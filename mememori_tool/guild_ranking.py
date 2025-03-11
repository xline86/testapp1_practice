from datetime import datetime
from pathlib import Path

import requests


def get_wgroup(world_id):
    """world_id(swww)が与えられた時、同じグループに属すすべてのworld_idを返す

    Args:
        world_id (int): world_id(swww)

    Returns:
        list: 同一グループに属するworld_idのリスト
        例: [1099, 1103, 1107, 1111]
    """
    url = "https://api.mentemori.icu/wgroups"
    response = requests.get(url)
    data = response.json()["data"]

    for group_data in data:
        if world_id in group_data["worlds"]:
            return group_data["worlds"]


def get_guildranking(world_id):
    """与えられたワールドのギルドランキングを入手する

    Args:
        world_id (int): swww

    Returns:
        list: ギルドの戦闘力に関するランキング
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/guild_ranking/latest"
    response = requests.get(url)
    data = response.json()["data"]

    bp = data["rankings"]["bp"]

    return bp


def get_group_guildranking(world_id):
    """world_idが属するグループのすべてのギルドランキングを結合する

    Args:
        world_id (int): world_id

    Returns:
        list: グループのギルドランキング
    """
    bp_group = []
    # for around_world_id in [1097, 1099, 1106, 1108]:
    for around_world_id in get_wgroup(world_id):
        bp_world = get_guildranking(around_world_id)

        # world_idの情報を追記
        for i in range(len(bp_world)):
            bp_world[i]["world_id"] = around_world_id

        bp_group += bp_world

    sorted_group_guildranking = sorted(bp_group, key=lambda x: x["bp"], reverse=True)

    return sorted_group_guildranking


def get_sorted_bp(sorted_bp, output=False):
    """group_guildrankingに関するdataを人間にわかりやすいよう整形する

    Args:
        sorted_bp (dictionary): data
    """
    sbody = ""
    sbody += datetime.now().isoformat(timespec="seconds") + "\n"
    sbody += "順位,\tworld_id,\tギルド名,\tギルド戦闘力\n"
    for index, guild in enumerate(sorted_bp):
        if index == 16 or index == 32 or index == 48:
            sbody += "----\n"
        sbody += f'{str(index + 1):>3}位,\t{int(str(guild["world_id"])[1:]):>3},\t{guild["name"]},\t{guild["bp"]}\n'

    # outputfile_path = Path(__file__).resolve().parent.joinpath("output.txt")
    # outputfile = open(outputfile_path, "w", encoding="utf-8")
    # outputfile.write(sbody)
    # outputfile.close

    if output:
        outputfile_path = Path(__file__).resolve().parent.joinpath("output.txt")
        with open(outputfile_path, "w", encoding="utf-8") as outputfile:
            outputfile.write(sbody)

    return sbody


if __name__ == "__main__":
    data = get_group_guildranking(1099)

    sbody = get_sorted_bp(data)
    print(sbody)
