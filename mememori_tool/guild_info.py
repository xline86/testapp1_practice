import cnum
import requests


def get_playerbpranking_and_playerinfo(world_id):
    """与えられたワールドのbpランキングとプレイヤー情報を入手する

    Args:
        world_id (int): swww

    Returns:
        tuple: プレイヤーランキングとプレイヤー情報
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/player_ranking/latest"
    response = requests.get(url)
    data = response.json()["data"]

    bpranking = data["rankings"]["bp"]
    player_info = data["player_info"]

    return (bpranking, player_info)


def get_bp50_playerid(bpranking):
    """与えられたワールドのbpランキングから上位50人のプレイヤーIDとそのbp, 順位を入手する

    Args:
        world_id (int): swww

    Returns:
        dict: 上位50人のプレイヤーIDとそのbp, 順位
    """

    bp50_playerid = {}
    for i in range(50):
        bp50_playerid[bpranking[i]["id"]] = {"bp": bpranking[i]["bp"], "order": i + 1}
        # bp50_playerid.append(bpranking[i]["id"])

    return bp50_playerid


def get_player_joinguild(bpranking, player_info, guild_id):
    """与えられたギルドに所属するランカーの情報を入手する

    Args:
        bpranking (list): bpランキング
        player_info (dict): プレイヤー情報
        guild_id (int): ギルドID

    Returns:
        list: ギルドメンバーの情報
    """

    ranker_joinguild = []
    bp50_playerid = get_bp50_playerid(bpranking).keys()
    for player_id in bp50_playerid:
        if player_info[str(player_id)]["guild_id"] == guild_id:
            ranker_joinguild.append(player_id)

    return ranker_joinguild


def get_ranker_info(player_info, player_id):
    """与えられたプレイヤーIDのプレイヤー情報を入手する

    Args:
        player_info (dict): プレイヤー情報
        player_id (int): プレイヤーID(top50のランカーのみ)

    Returns:
        dict: ランカーの情報
    """
    ranker_info = {}
    ranker_info["name"] = player_info[str(player_id)]["name"]
    ranker_info["bp"] = player_info[str(player_id)]["bp"]

    bp50_playerid = get_bp50_playerid(bpranking)
    ranker_info["order"] = bp50_playerid[player_id]["order"]
    ranker_info["guild_name"] = player_info[str(player_id)]["guild_name"]

    return ranker_info


def get_ranker_info_joinguild(player_info, guild_id):
    """与えられたギルドに所属するランカーの情報を入手する

    Args:
        player_info (dict): プレイヤー情報
        player_id (int): プレイヤーID
    """

    ranker_info_joinguild = []
    player_joinguild = get_player_joinguild(bpranking, player_info, guild_id)
    for id in player_joinguild:
        ranker_info_joinguild.append(get_ranker_info(player_info, id))

    return ranker_info_joinguild


def print_ranker_info_joinguild(player_info, guild_id):
    """与えられたギルドに所属するランカーの情報を表示する

    Args:
        player_info (dict): プレイヤー情報
        player_id (int): プレイヤーID
    """

    sbody = (
        f"ギルド名: {get_guild_name(guild_info, guild_id)}に所属するランカーの情報\n"
    )
    ranker_info_joinguild = get_ranker_info_joinguild(player_info, guild_id)
    for ranker_info in ranker_info_joinguild:
        sbody += f"順位: {ranker_info['order']}, プレイヤー名: {ranker_info['name']}, BP: {cnum.jp(ranker_info['bp'])}\n"

    print(sbody)


def get_guildinfo(world_id):
    """与えられたワールドのギルド情報を入手する

    Args:
        world_id (int): swww

    Returns:
        dict: ギルド情報
    """
    url = "https://api.mentemori.icu/" + str(world_id) + "/guild_ranking/latest"
    response = requests.get(url)
    data = response.json()["data"]

    guild_info = data["guild_info"]

    return guild_info


def get_guild_name(guild_info, guild_id):
    """与えられたギルドIDのギルド名を入手する

    Args:
        guild_info (dict): ギルド情報
        guild_id (int): ギルドID

    Returns:
        str: ギルド名
    """
    return guild_info[str(guild_id)]["name"]


if __name__ == "__main__":
    world_id = 1099
    guild_id = 196765134099
    (bpranking, player_info) = get_playerbpranking_and_playerinfo(world_id)
    guild_info = get_guildinfo(world_id)

    print_ranker_info_joinguild(player_info, guild_id)

    # print(get_guild_name(guild_info, 199652669099))
