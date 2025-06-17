import os
import cnum
from datetime import datetime
from mememori_tool import mentemorimori_tool


import discord
from discord import app_commands
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("TOKEN")
APP_NAME = os.getenv("APP_NAME")
ENV = os.getenv("ENV", "production")
AUTHOR_NAME = os.getenv("AUTHOR_NAME")
AUTHOR_BELONGTO = os.getenv("AUTHOR_BELONGTO")

# Discord クライアント設定
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# 定数定義
SERVER_OFFSET = {
    "jp": 1000,
    "kr": 2000,
    "asia": 3000,
    "na": 5000,
    "europe": 5000,
    "global": 6000,
}

GVG_CLASSES = {
    1: {"name": "グランドマスター", "range": range(0, 16)},
    2: {"name": "エキスパート", "range": range(16, 32)},
    3: {"name": "エリート", "range": range(32, 48)},
    4: {"name": "other", "range": range(48, 64)},
}


# イベント: 起動時
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    await tree.sync()


# コマンド: /help
@tree.command(name="help", description="ヘルプメッセージを表示します")
async def help_command(interaction: discord.Interaction):
    help_message = (
        "この discord bot は、ギルドランキングやギルド情報を取得するためのコマンドを提供します。\n"
        "以下のコマンドが利用可能です:\n"
        "\n"
        "/ranking -- グループにおけるギルドランキングを表示\n"
        "-# 使用例: `/ranking world_number:99 gvg_class:グランドマスター`\n"
        "/guildinfo -- 指定したワールドのギルドの詳細情報を表示\n"
        "-# 使用例: `/guildinfo world_number:99 guild_id:494634944099`\n"
        "/help -- このヘルプメッセージを表示\n"
        "\n"
        "情報は全て[メンテもりもり](https://mentemori.icu/)から取得しています\n"
        "コマンドが実行されるたびにメンテもりもりのAPIを呼び出すため、APIの負荷を考慮して適切に使用してください。\n"
        "\n"
        f"この discord bot は{AUTHOR_BELONGTO}の{AUTHOR_NAME}によって作成されました\n"
    )
    await interaction.response.send_message(help_message)


# ユーティリティ関数
def resolve_world_id(server: str, world_number: int) -> int:
    key = server.lower()
    if key not in SERVER_OFFSET:
        raise ValueError(f"不正なサーバー名です: {server}")
    return SERVER_OFFSET[key] + world_number


def format_guild_ranking(ranking_data: dict, gvg_class_id: int) -> str:
    ranking_list = ranking_data["ranking"]
    world_ids = ranking_data["worlds"]
    group_id = ranking_data["group_id"]
    gvg_class_info = GVG_CLASSES[gvg_class_id]

    worlds_str = " ".join([f"w{str(world_id)[1:]}" for world_id in world_ids])
    header = (
        f"-# {datetime.now().isoformat(timespec='seconds')}\n"
        + f"group_id: {group_id} ({worlds_str}) におけるギルドランキング\n{gvg_class_info['name']} クラス\n"
    )

    lines = [header]
    for i in gvg_class_info["range"]:
        if i >= len(ranking_list):
            break
        guild = ranking_list[i]
        world_suffix = str(guild["world_id"])[1:]
        lines.append(
            f'{i + 1:>3}位,\t{guild["name"]}\n'
            f'-#    (w{world_suffix}, guild_id: {guild["id"]}), \t'
            f'{guild["num_members"]}人, \t'
            f'bp: {cnum.jp(guild["bp"])}\n'
        )

    return "".join(lines)


# コマンド: /ranking
@tree.command(
    name="ranking", description="サーバーが属するグループのギルドランキングを表示"
)
@app_commands.describe(
    world_number="例: w99なら99を入力",
    gvg_class="ギルドクラスを選択",
    server="例: jp, kr, asia, na, europe, global",
)
@app_commands.choices(
    gvg_class=[
        app_commands.Choice(name=v["name"], value=k) for k, v in GVG_CLASSES.items()
    ]
)
async def ranking(
    interaction: discord.Interaction,
    world_number: int,
    gvg_class: app_commands.Choice[int],
    server: str = "jp",
):
    await interaction.response.send_message("処理中...")
    msg = await interaction.original_response()

    try:
        world_id = resolve_world_id(server, world_number)
        data = mentemorimori_tool.get_group_bp_guild_ranking(world_id)
        response = format_guild_ranking(data, gvg_class.value)
    except Exception as e:
        response = f"エラーが発生しました: {str(e)}"

    await msg.edit(content=response)


# コマンド: /guildinfo
@tree.command(name="guildinfo", description="ギルドの詳細情報を表示")
@app_commands.describe(
    world_number="例: w99なら99を入力",
    guild_id="/rankingコマンドを見て入力",
    server="例: jp, kr, asia, na, europe, global",
)
async def guildinfo(
    interaction: discord.Interaction,
    world_number: int,
    guild_id: int,
    server: str = "jp",
):
    try:
        world_id = resolve_world_id(server, world_number)
        detail = mentemorimori_tool.output_guild_info_detail(world_id, guild_id)
    except Exception as e:
        detail = f"エラーが発生しました: {str(e)}"

    await interaction.response.send_message(detail)


if ENV == "practice":
    import practice_commands

    practice_commands.register_practice_commands(tree)


# ボットを起動
client.run(TOKEN)
