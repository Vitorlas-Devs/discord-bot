import asyncio
import calendar
import datetime
from pathlib import Path
import dotenv
import pytz
import os
import re
from typing import Optional, List, Literal
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv

load_dotenv()

img_folder = "img\\"

MY_GUILD = discord.Object(id=1015997406443229204)
TOKEN = os.getenv("DISCORD_TOKEN")

# START CODING HERE


class Bot(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix, intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = Bot(command_prefix="-", intents=intents)


@bot.event
async def on_ready():

    global LYEDLIK, OT_ROLE, DEV_ROLE, TAG_ROLE, DÖK_ROLE, JEDLIK_ROLE, VETERÁN_ROLE, KÜLSŐS_ROLE, PORTA_CHANNEL, LOG_CHANNEL, OWNER
    LYEDLIK = bot.get_guild(1015997406443229204)

    OT_ROLE = LYEDLIK.get_role(1018451182131355728)
    DEV_ROLE = LYEDLIK.get_role(1018451781774225470)
    TAG_ROLE = LYEDLIK.get_role(1019936616262942771)
    DÖK_ROLE = LYEDLIK.get_role(1015998890102763602)
    JEDLIK_ROLE = LYEDLIK.get_role(1019649131712618558)
    VETERÁN_ROLE = LYEDLIK.get_role(1019649352374947890)
    KÜLSŐS_ROLE = LYEDLIK.get_role(1019649458461495356)

    PORTA_CHANNEL = LYEDLIK.get_channel(1015997407265304688)
    LOG_CHANNEL = LYEDLIK.get_channel(1019666689610227834)

    OWNER = bot.get_user(361534796830081024)
    # await bot.change_presence(
    #     status=discord.Status.online,
    #     activity=discord.Streaming(
    #         name="Matekházi írás", url="https://www.twitch.tv/discord"
    #     ),
    # )
    print(f"Logged in as {bot.user} in {LYEDLIK.name} (⌐■_■)")
    print("------")


mod_group = app_commands.Group(name="mod", description="Mod group")
dev_group = app_commands.Group(name="dev", description="Dev group")


@app_commands.default_permissions(manage_messages=True)
class ModGroup(app_commands.Group):
    bot.tree.add_command(mod_group)


@app_commands.default_permissions(view_audit_log=True)
class DevGroup(app_commands.Group):
    bot.tree.add_command(dev_group)


@bot.event
async def on_member_join(member):
    await member.add_roles(TAG_ROLE)


@bot.event
async def on_scheduled_event_update(before, after):
    if (
        after.name in ["OT Gyűlés", "Teadu"]
        and after.status == discord.EventStatus.completed
    ):
        image = await after.cover_image.read()
        await LYEDLIK.create_scheduled_event(
            name=after.name,
            description="",
            start_time=after.start_time + datetime.timedelta(days=7),
            end_time=after.end_time + datetime.timedelta(days=7),
            image=image,
            location=after.location,
        )
        await event_invite(after)


class Button1Modal(ui.Modal, title="Név megadása"):
    name = ui.TextInput(
        label="Név",
        required=True,
        placeholder="Bartók Béla",
        style=discord.TextStyle.paragraph,
    )
    grade = ui.TextInput(label="Osztály", placeholder="9A", required=False)

    async def on_submit(self, inter: discord.Interaction):
        grade_str = re.sub("[\W_]+", "", self.grade.value).upper().strip()
        await inter.user.edit(nick=self.name.value)
        if len(grade_str) < 2:
            await inter.response.send_message(
                "Név megadva osztály nélkül!", ephemeral=True
            )
        else:
            role = discord.utils.get(LYEDLIK.roles, name=grade_str)
            if role in LYEDLIK.roles:
                await inter.user.add_roles(role)
            else:
                role = await LYEDLIK.create_role(name=grade_str)
                await role.edit(position=DEV_ROLE.position - 2)
                await inter.user.add_roles(role)
            await inter.response.send_message(
                "Sikeres név megadás osztállyal!", ephemeral=True
            )


class Button1View(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="😎 Név megadása",
        style=discord.ButtonStyle.primary,
    )
    async def button_callback(
        self, inter: discord.Interaction, button: discord.ui.Button
    ):
        await inter.response.send_modal(Button1Modal())


class Dropdown1(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Jedlik", description="Módos Gábor a királyunk", emoji="🔵"
            ),
            discord.SelectOption(
                label="Veterán",
                description="Voltam jedlikes, már nem járok oda",
                emoji="🟢",
            ),
            discord.SelectOption(
                label="Külsős",
                description="Nem vagyok jedlikes és nem is voltam",
                emoji="🟩",
            ),
        ]
        super().__init__(
            placeholder="Add meg a jedlikességedet!",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: discord.Interaction):
        if "Jedlik" in self.values:
            await inter.user.add_roles(JEDLIK_ROLE)
        if "Veterán" in self.values:
            await inter.user.add_roles(VETERÁN_ROLE)
        if "Külsős" in self.values:
            await inter.user.add_roles(KÜLSŐS_ROLE)
        await inter.response.send_message(
            f"A választásaid rögzítve: {self.values}", ephemeral=True
        )


class Dropdown2(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="DEV", description="(●'◡'●)", emoji="🔴"),
            discord.SelectOption(label="DÖK", description="DÖK-ös vagyok", emoji="🟡"),
        ]
        super().__init__(
            placeholder="Válaszd ki azokat, amelyek rádillenek *többes szám*",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, inter: discord.Interaction):
        if "DÖK" in self.values:
            await inter.user.add_roles(DÖK_ROLE)
        if "DEV" in self.values:
            await inter.user.add_roles(DEV_ROLE)
        await inter.response.send_message(
            f"A választásaid rögzítve: {self.values}", ephemeral=True
        )


class DropdownView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown2())
        self.add_item(Dropdown1())


class Button2View(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🟣 OT kérelem", style=discord.ButtonStyle.secondary)
    async def button_callback(
        self, inter: discord.Interaction, button: discord.ui.Button
    ):
        global USER_TO_OT
        USER_TO_OT = inter.user

        e = discord.Embed(
            title="OT kérelem",
            description=USER_TO_OT.mention,
            color=discord.Color.purple(),
        )
        e.set_author(name=USER_TO_OT.name, icon_url=USER_TO_OT.avatar.url)
        await LOG_CHANNEL.send(
            OWNER.mention,
            embed=e,
            view=Button3View(),
        )
        await inter.response.send_message("Kérelem elküldve!", ephemeral=True)


class Button3View(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👍 Elfogadás", style=discord.ButtonStyle.success)
    async def button_callback(
        self, inter: discord.Interaction, button: discord.ui.Button
    ):
        if OT_ROLE in inter.user.roles or inter.user == OWNER:
            await USER_TO_OT.add_roles(OT_ROLE)
            await inter.response.send_message(
                f"{USER_TO_OT.mention} OT kérelmét {inter.user.mention} elfogadta",
                ephemeral=False,
            )
            self.stop()

    @discord.ui.button(label="👎 Elvetés", style=discord.ButtonStyle.danger)
    async def button_callback_decline(
        self, inter: discord.Interaction, button: discord.ui.Button
    ):
        if OT_ROLE in inter.user.roles or inter.user == OWNER:
            await inter.response.send_message(
                f"{USER_TO_OT.mention} OT kérelmét {inter.user.mention} elutasította",
                ephemeral=False,
            )
            self.stop()


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Verification embed in #porta for new users"""
    await ctx.message.delete()
    embed1 = discord.Embed(
        title="Üdv a Jedlik szerverén!",
        description=":white_small_square: **Ahhoz, hogy hozzáférj a szerver többi részéhez is, a következő \nlépéseken kell végigmenj:**\n\n:one: - Teljes név és osztály megadása\n:two: - Szerver szerepkörök kiválasztása",
        color=0x2F3136,
    )
    await PORTA_CHANNEL.send(
        file=discord.File(
            img_folder + "jedlik_banner.png", filename="jedlik_banner.png"
        ),
        embed=embed1,
    )

    embed6 = discord.Embed(
        title=":purple_square: - OT vagyok",
        description=":white_small_square: Csak OT tagoknak: katt a gombra!",
        color=discord.Color.purple(),
    )
    view5 = Button2View()
    await PORTA_CHANNEL.send(embed=embed6, view=view5)

    embed2 = discord.Embed(
        title=":one: - Teljes név és osztály megadása",
        description=":white_small_square: Ez az üzenet alatt lévő gombra kattintás után a felugró ablakban adhatod meg a neved.\n\n__Az osztályt csak a jedlikeseknek kell beírni,__ ha nem jársz ide akkor hagyd üresen!",
        color=0xED033D,
    )
    view1 = Button1View()
    await PORTA_CHANNEL.send(embed=embed2, view=view1)

    embed5 = discord.Embed(
        title=":two: - Szerepkörök kiválasztása",
        description=f":white_small_square: Ez az üzenet alatt lévő menüben választhatod ki a hozzád tartozó Role-okat.\n\n**Kiegészítő Role-ok:**\n{DEV_ROLE.mention}: Ha érdekel a Python és a Discord botok programozása, akkor itt csatlakozhatsz a Lyedlik Devs-hez!\n{DÖK_ROLE.mention}: DÖK-ös szobákhoz hozzáférés\n\n**Jedlikesség mértéke:**\n:warning: Ezt add meg utoljára thanks.\n:information_source: Ebből egy választása kötelező a regisztrációhoz!\n{JEDLIK_ROLE.mention}: Jelenleg jedlikes tanulók\n{VETERÁN_ROLE.mention}: Volt jedlikes tanulók\n{KÜLSŐS_ROLE.mention}: Nem jedlikesek",
        color=0x0596F7,
    )
    view4 = DropdownView()
    await PORTA_CHANNEL.send(embed=embed5, view=view4)


@bot.tree.command()
async def hello(inter: discord.Interaction):
    """Hi"""
    await inter.response.send_message(
        f"Szeva, {inter.user.mention}",
        allowed_mentions=discord.AllowedMentions(users=False),
    )


@bot.tree.command()
@app_commands.describe(member="A tag, akinek a csatlakozási dátumát szeretnéd megnézni")
async def joined(inter: discord.Interaction, member: Optional[discord.Member] = None):
    """Show when a member joined the server"""
    member = member or inter.user
    await inter.response.send_message(
        f"> {member} csatlakozási ideje: {discord.utils.format_dt(member.joined_at)}"
    )


@bot.tree.context_menu(name="Csatlakozás ideje")
async def show_join_date(inter: discord.Interaction, member: discord.Member):
    """Show when a member joined the server"""
    await inter.response.send_message(
        f"> {member} csatlakozási ideje: {discord.utils.format_dt(member.joined_at)}"
    )


@dev_group.command()
@app_commands.describe(
    color="embed színe",
    title="embed címe",
    description="embed leírása",
)
@app_commands.checks.has_permissions(view_audit_log=True)
async def embed(
    inter: discord.Interaction,
    color: Literal["dark_theme", "red", "green", "fuchsia", "yellow"],
    title: Optional[str] = "Embed",
    *,
    description: Optional[str] = None,
):
    """Send custom embed"""
    colors = {
        "dark_theme": "0x36393F",
        "green": "0x57F287",
        "red": "0xED4245",
        "fuchsia": "0xEB459E",
        "yellow": "0xFEE75C",
    }
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.from_str(colors[color]),
    )
    embed.set_footer(
        text=f"{bot.user.display_name} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=bot.user.display_avatar.url,
    )
    await inter.response.send_message(embed=embed)


@mod_group.command()
@app_commands.describe(
    amount="A törölni kívánt üzenetek száma (alapértelmezett: 1)",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(inter: discord.Interaction, amount: Optional[int] = 1):
    """Delete a specified amount of messages"""
    await inter.channel.purge(limit=amount)
    await asyncio.sleep(3)
    await inter.response.send_message(f"{amount} üzenet törölve.", ephemeral=False)
    await inter.delete_original_response()


@bot.tree.context_menu(name="Üzenet Jelentése")
async def report_message(inter: discord.Interaction, message: discord.Message):
    """Report a message and send it to the log channel"""
    await inter.response.send_message(
        f"Köcce {message.author.mention}, a jelentés rögzítve lett.", ephemeral=True
    )

    embed = discord.Embed(title="Jelentett üzenet")
    if message.content:
        embed.description = message.content

    embed.set_author(
        name=message.author.display_name, icon_url=message.author.display_avatar.url
    )
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(
        discord.ui.Button(
            label="Ugrás az üzenethez",
            style=discord.ButtonStyle.url,
            url=message.jump_url,
        )
    )

    await LOG_CHANNEL.send(embed=embed, view=url_view)


@dev_group.command()
@app_commands.checks.has_permissions(view_audit_log=True)
async def slash_clear(inter: discord.Interaction):
    """Remove all slash commands from the server, used for Test bots to avoid overcrowding the server"""
    await inter.response.send_message(
        "Slash command-ok eltávolítva.\nA Bot készen áll a leállításra.", ephemeral=True
    )
    bot.tree.clear_commands(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)


@dev_group.command()
@app_commands.checks.has_permissions(view_audit_log=True)
async def setup_events(inter: discord.Interaction):
    """Set the recurring events: OT and Teadu"""
    await inter.response.defer(ephemeral=False, thinking=True)

    for event in inter.guild.scheduled_events:
        if event.name in ["OT Gyűlés", "Teadu"]:
            await event.delete()

    # Timezone error, subtract 44 minutes
    ot_event = await LYEDLIK.create_scheduled_event(
        name="OT Gyűlés",
        description="",
        start_time=datetime.datetime(
            year=datetime.date.today().year,
            month=datetime.date.today().month,
            day=(
                datetime.date.today()
                + datetime.timedelta((2 - datetime.date.today().weekday()) % 7 + 1)
            ).day,
            hour=14,
            minute=16,
            second=0,
            microsecond=0,
            tzinfo=pytz.timezone("Europe/Budapest"),
        ),
        end_time=datetime.datetime(
            year=datetime.date.today().year,
            month=datetime.date.today().month,
            day=(
                datetime.date.today()
                + datetime.timedelta((2 - datetime.date.today().weekday()) % 7 + 1)
            ).day,
            hour=15,
            minute=16,
            second=0,
            microsecond=0,
            tzinfo=pytz.timezone("Europe/Budapest"),
        ),
        image=Path(img_folder + "jedlik_banner.png").read_bytes(),
        location="Diáktanya (111-es terem)",
    )
    teadu_event = await LYEDLIK.create_scheduled_event(
        name="Teadu",
        description="",
        start_time=datetime.datetime(
            year=datetime.date.today().year,
            month=datetime.date.today().month,
            day=(
                datetime.date.today()
                + datetime.timedelta((3 - datetime.date.today().weekday()) % 7 + 1)
            ).day,
            hour=14,
            minute=16,
            second=0,
            microsecond=0,
            tzinfo=pytz.timezone("Europe/Budapest"),
        ),
        end_time=datetime.datetime(
            year=datetime.date.today().year,
            month=datetime.date.today().month,
            day=(
                datetime.date.today()
                + datetime.timedelta((3 - datetime.date.today().weekday()) % 7 + 1)
            ).day,
            hour=15,
            minute=16,
            second=0,
            microsecond=0,
            tzinfo=pytz.timezone("Europe/Budapest"),
        ),
        image=Path(img_folder + "jedlik_banner.png").read_bytes(),
        location="Diáktanya (111-es terem)",
    )

    await event_invite(ot_event)
    await event_invite(teadu_event)

    await inter.followup.send(f"OT és Teadu eventek beállítva.", ephemeral=False)


async def event_invite(event: discord.ScheduledEvent):
    """Adds the event to an invite link (if there isn't none, create a new one) and send it to the log channel"""
    invite = None
    for channel_invite in await LOG_CHANNEL.invites():
        if channel_invite.inviter == bot.user:
            invite = channel_invite
            break

    if not invite:
        invite = await LOG_CHANNEL.create_invite()

    invite.set_scheduled_event(event)
    await LOG_CHANNEL.send(
        f"**Új esemény felvéve: {event.name}, {discord.utils.format_dt(event.start_time)}**\n{invite.url}"
    )


class RoleGiverButtonView(ui.View):
    @discord.ui.button(label=f"▶️ Kérem", style=discord.ButtonStyle.primary)
    async def button_callback(
        self, inter: discord.Interaction, button: discord.ui.Button
    ):
        await inter.user.add_roles(ROLEGIVER_ROLE)
        await inter.response.send_message(
            f"{inter.user.mention}, hozzáadva: {ROLEGIVER_ROLE.mention}",
            ephemeral=True,
        )


@dev_group.command()
@app_commands.describe(
    role="A megadandó Role",
)
@app_commands.checks.has_permissions(view_audit_log=True)
async def role_giver(inter: discord.Interaction, role: discord.Role):
    """Send an embed with a button to request a role"""
    e = discord.Embed(
        title=f"Kattints a gombra a {role.name} Role-ért!",
        description=role.mention,
        color=role.color,
    )
    global ROLEGIVER_ROLE
    ROLEGIVER_ROLE = role
    e.set_author(name=inter.user.display_name, icon_url=inter.user.display_avatar.url)
    e.set_footer(
        text=f"{bot.user.display_name} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=bot.user.display_avatar.url,
    )
    await inter.response.send_message(
        embed=e, view=RoleGiverButtonView(), ephemeral=False
    )


# Not working
@bot.command()
@commands.has_permissions(view_audit_log=True)
async def sync(ctx):
    """Reload all the slash commands"""
    await ctx.message.delete()
    msg = await ctx.send("`Slash command-ok visszatöltése...`")
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    await msg.edit(content="`Kész.`")
    await asyncio.sleep(3)
    await msg.delete()


bot.run(TOKEN)
