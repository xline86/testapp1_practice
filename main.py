import codecs
import io
import os
import sys

from datetime import datetime

import discord
from discord import app_commands
from dotenv import load_dotenv

import cnum
from mememori_tool import mentemorimori_tool

# === 環境変数読み込み ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
APP_NAME = os.getenv("APP_NAME")

# === Discord クライアント設定 ===
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# === 定数定義 ===
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


# === イベント: 起動時 ===
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    await tree.sync()


# === ユーティリティ関数 ===
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
    header = f"group_id: {group_id} ({worlds_str}) におけるギルドランキング\n{gvg_class_info['name']} クラス\n"

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

    lines.append(f"-# {datetime.now().isoformat(timespec='seconds')}\n")
    return "".join(lines)


# === コマンド: /ranking ===
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


# === コマンド: /guildinfo ===
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


# === コマンド: /sync_reload ===
@tree.command(name="sync_reload", description="スラッシュコマンドを手動で同期します")
async def sync_reload(interaction: discord.Interaction):
    await interaction.response.send_message("同期中...", ephemeral=True)
    msg = await interaction.original_response()

    synced = await tree.sync()
    await msg.edit(content=f"{len(synced)} 個のスラッシュコマンドを同期しました")


if APP_NAME == "testapp1_practice":

    @tree.command(
        name="send_txt",
        description="テキストファイルを送信する",
    )
    async def send_txt(interaction: discord.Interaction):
        sendtext = "これはテストです。\nテキストファイルを送信できることを確かめるために作成されました。"

        sys.stdout = codecs.getwriter("utf_8")(sys.stdout)
        with io.StringIO(sendtext) as f:
            await interaction.channel.send(file=discord.File(f, "send.txt"))

    @tree.command(
        name="test",
        description="テスト用コマンド",
    )
    @app_commands.describe(
        text="テスト用のテキストを入力してください",
    )
    @app_commands.choices(
        text=[
            app_commands.Choice(name="テスト1", value=1),
            app_commands.Choice(name="テスト2", value=2),
            app_commands.Choice(name="テスト3", value=3),
        ]
    )
    async def test(
        interaction: discord.Interaction,
        text: app_commands.Choice[int],
        # text: app_commands.Choice[int] = app_commands.Choice(name="テスト1", value=1),
        # text: int = 1,
    ):
        await interaction.response.send_message(
            f"テスト用コマンドです\nあなたの選択: {text.name}（値: {text.value}）"
        )

        print(text, type(text))

    @tree.command(
        name="hello",
        description="挨拶する",
    )
    async def hello(
        interaction: discord.Interaction, sendtext: str = f"{APP_NAME} より心を込めて"
    ):

        name = interaction.user.name
        await interaction.response.send_message(
            f"{name} さん, こんにちは AAAAA\n" + str(sendtext)
        )


# ボットを起動
client.run(TOKEN)
