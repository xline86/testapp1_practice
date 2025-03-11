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
    response = requests.get(url)
    data = response.json()["data"]

    for group_data in data:
        if world_id in group_data["worlds"]:
            return group_data["worlds"]

    return None


def get_guildranking(world_id: int) -> list:
    """与えられたワールドのguild rankingを入手する

    Args:
        world_id (int): swww

    Returns:
        list: ギルドの戦闘力に関するランキング
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/guild_ranking/latest"
    response = requests.get(url)
    data = response.json()["data"]

    return data


def get_bp20_guild_ranking(data: list) -> list:
    """guild rankinから戦闘力top20のrankingを取得する

    Args:
        data (list): guild ranking

    Returns:
        list: 戦闘力top20のguild ranking
    """

    # 戦闘力top20のguild_idをランキング順に取得
    bp20_guild_id = [data["rankings"]["bp"][i]["id"] for i in range(20)]

    bp20_guild_info = []
    for i in range(20):
        bp20_guild_info.append(data["guild_info"][str(bp20_guild_id[i])])

        # guild_infoにはworld_idが含まれていないので追加
        bp20_guild_info[i]["world_id"] = data["world_id"]

    # outputfile_path = Path(__file__).resolve().parent.joinpath("output.json")
    # with open(outputfile_path, "w", encoding="utf-8") as outputfile:
    #     json.dump(bp20_guild_info, outputfile, ensure_ascii=False)

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
        data = get_guildranking(around_world_id)
        group_bp_ranking += get_bp20_guild_ranking(data)

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
        if index == 16 or index == 32 or index == 48:
            sbody += "----\n"

        # sbody += f"{guild_info["name"]}\n"
        sbody += (
            f'{str(index + 1):>3}位,\t{guild_info["name"]}\n'
            + f'    (w{str(guild_info["world_id"])[1:]}, guild_id: {guild_info["id"]}), \t'
            + f'{guild_info["num_members"]}人, \t'
            + f'bp: {cnum.jp(guild_info["bp"])}\n'
        )

        if index == length - 1:
            break

    if is_export:
        if export_path is None:
            outputfile_path = Path(__file__).resolve().parent.joinpath("output.txt")
        else:
            outputfile_path = Path(export_path)

        with open(outputfile_path, "w", encoding="utf-8") as outputfile:
            outputfile.write(sbody)

    return sbody


if __name__ == "__main__":
    world_id = 1099
    output_bp_ranking(1099, is_export=True)
