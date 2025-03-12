import json
from datetime import datetime
from pathlib import Path

import cnum
import requests


def get_wgroup(world_id: int):
    """world_id(swww)が与えられた時、同じグループに属すすべてのworld_idを返す

    Args:
        world_id (int): world_id(swww)

    Returns:
        list: 同一グループに属するworld_idのリスト
        例: [1099, 1103, 1107, 1111]
    """
    url = "https://api.mentemori.icu/wgroups"
    response = requests.get(url).json()

    if response["status"] != 200:
        print("API Error: get_wgroup")
        return None

    data = response["data"]

    for group_data in data:
        if world_id in group_data["worlds"]:
            return group_data["worlds"]

    return None


def get_bp50_player_ranking(world_id: int, is_export=False) -> list:
    """与えられたワールドのplayer rankingを入手する

    Args:
        world_id (int): swww

    Returns:
        list: プレイヤーの戦闘力に関するランキング
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/player_ranking/latest"
    response = requests.get(url).json()
    data = response["data"]

    # 戦闘力 top50 の player_id をランキング順に取得
    bp50_player_id = [data["rankings"]["bp"][i]["id"] for i in range(50)]

    bp50_player_info = []
    for i in range(50):
        bp50_player_info.append(data["player_info"][str(bp50_player_id[i])])

        # guild_infoにはworld_idが含まれていないので追加
        bp50_player_info[i]["world_id"] = data["world_id"]

    if is_export:
        outputfile_path = Path(__file__).resolve().parent.joinpath("output.json")
        with open(outputfile_path, "w", encoding="utf-8") as outputfile:
            json.dump(bp50_player_info, outputfile, ensure_ascii=False)

    return bp50_player_info


def get_bp20_guild_ranking(world_id: int) -> list:
    """与えられたワールドの guild bp ranking top 20 を入手する

    Args:
        world_id (int): swww

    Returns:
        list: ギルドの戦闘力に関するランキング
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/guild_ranking/latest"
    response = requests.get(url).json()
    data = response["data"]

    # 戦闘力top20のguild_idをランキング順に取得
    bp20_guild_id = [data["rankings"]["bp"][i]["id"] for i in range(20)]

    bp20_guild_info = []
    for i in range(20):
        bp20_guild_info.append(data["guild_info"][str(bp20_guild_id[i])])

        # guild_infoにはworld_idが含まれていないので追加
        bp20_guild_info[i]["world_id"] = data["world_id"]

    return bp20_guild_info


def get_group_bp_guild_ranking(world_id):
    """world_idが属するグループのすべてのギルドランキングを統合する

    Args:
        world_id (int): world_id

    Returns:
        list: グループのギルドランキング
    """
    group_bp_ranking = []
    for around_world_id in get_wgroup(world_id):
        group_bp_ranking += get_bp20_guild_ranking(around_world_id)

    group_bp_ranking.sort(key=lambda x: x["bp"], reverse=True)

    return group_bp_ranking


def output_bp_ranking(world_id, length=50, is_export=False, export_path=None) -> str:
    """group_guildrankingに関するdataを人間にわかりやすいよう整形する

    Args:
        bp_ranking (dictionary): data
    """
    bp_ranking = get_group_bp_guild_ranking(world_id)

    sbody = ""
    sbody += datetime.now().isoformat(timespec="seconds") + "\n"
    sbody += "順位,\tworld_id,\tギルド名\n"
    for index, guild_info in enumerate(bp_ranking):
        if index == length:
            break

        if index == 16 or index == 32 or index == 48:
            sbody += "----\n"

        # sbody += f"{guild_info["name"]}\n"
        sbody += (
            f'{str(index + 1):>3}位,\t{guild_info["name"]}\n'
            + f'    (w{str(guild_info["world_id"])[1:]}, guild_id: {guild_info["id"]}), \t'
            + f'{guild_info["num_members"]}人, \t'
            + f'bp: {cnum.jp(guild_info["bp"])}\n'
        )

    if is_export:
        if export_path is None:
            outputfile_path = Path(__file__).resolve().parent.joinpath("output.txt")
        else:
            outputfile_path = Path(export_path)

        with open(outputfile_path, "w", encoding="utf-8") as outputfile:
            outputfile.write(sbody)

    return sbody


def get_guild_info_detail(world_id, guild_id):
    """与えられたギルドに関する詳細な情報を入手する

    Args:
        world_id (int): swww
        guild_id (int): ギルドID

    Returns:
        dict: ギルド情報詳細
    """

    guild_info_detail = {"guild_info": None, "join_ranker": {}}

    bp20_guild_ranking = get_bp20_guild_ranking(world_id)
    for guild_info in bp20_guild_ranking:
        if guild_info["id"] == guild_id:
            guild_info_detail["guild_info"] = guild_info
            break

    if guild_info_detail["guild_info"] is None:
        return None

    bp50_player_ranking = get_bp50_player_ranking(world_id)
    for index, player_info in enumerate(bp50_player_ranking):
        # print(index, player_info["name"])

        if player_info["guild_id"] == guild_id:
            guild_info_detail["join_ranker"][str(index + 1)] = player_info

    return guild_info_detail


if __name__ == "__main__":
    world_id = 1099
    guild_id = 494634944099

    # output_bp_ranking(1099, is_export=True, length=16)

    # get_bp50_player_ranking(world_id, is_export=True)

    guild_info_detail = get_guild_info_detail(world_id, guild_id)
    outputfile_path = Path(__file__).resolve().parent.joinpath("output.json")
    with open(outputfile_path, "w", encoding="utf-8") as outputfile:
        json.dump(guild_info_detail, outputfile, ensure_ascii=False)
