
import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta
REQUIRED_ROLE = "1288077774468284418"
# create / load the stats JSON file
if os.path.exists("stats.json"):
    with open("stats.json", "r") as f:
        content = f.read().strip()
        if content:
            stats = json.loads(content)
        else:
            stats = {}
else:
    stats = {}
# bot settings shit idk really
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="g.", intents=intents)

# prevent gay lgbt people from using this command anywhere (replace this)
ALLOWED_CHANNEL_ID = 1331733707370790982 

# save stats to json (this is bad imo atleast)
def save_stats():
    with open("stats.json", "w") as f:
        json.dump(stats, f)


def ensure_user(user_id):
    if str(user_id) not in stats:
        stats[str(user_id)] = {"money": 200, "last_daily": None}
        

    

@bot.command(name="commands")
async def commands(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    commands_list = """
**Epic Casino Bot 42069 No Way !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:**
- `g.daily`: Claim your daily 200 dollars for free!!!!!!!!.
- `g.slots <bet>`: Play the slot machine.
- `g.blackjack <bet>`: Play a game of blackjack against the bot.
- `g.cointoss <bet> <heads/tails>`: Bet on a coin toss.
- `g.leaderboard`: View the top 10 richest players.
- `g.gift <@user> <amount>`: Gift money to another user.
- `g.nigger`: Check how black you are or someone else is.
- `g.duel <@user> <bet>`: Challenge another user to a blackjack duel.
"""
    await ctx.send(commands_list)
    # check how black u are 
@bot.command()
async def nigger(ctx):

    smartness = random.randint(1, 100)
    
    if ctx.message.mentions:
        mentioned_user = ctx.message.mentions[0].mention
        await ctx.send(f"{mentioned_user} is {smartness}% a nigger!")
    else:
        await ctx.send(f"You are  {smartness}% a nigger!")

# gambling part 1
@bot.command()
async def slots(ctx, bet: int):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    user_id = str(ctx.author.id)
    ensure_user(user_id)
    user_data = stats[user_id]

    if bet <= 0:
        await ctx.send("Bet must be a positive number.")
        return
    if user_data["money"] < bet:
        await ctx.send("You don't have enough money to make this bet.")
        return

    symbols = ["🍒", "🍋", "🍇", "🍊", "🔔", "⭐"]
    result = [random.choice(symbols) for _ in range(3)]
    win = len(set(result)) == 1

    if win:
        winnings = bet * 5
        user_data["money"] += winnings
        outcome = f"You won {winnings} dollars! 🎉"
    else:
        user_data["money"] -= bet
        outcome = "You lost your bet. Better luck next time!"

    save_stats()
    await ctx.send(f"{' | '.join(result)}\n{outcome} You now have {user_data['money']} dollars.")
# claim daily shit
@bot.command()
async def daily(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    user_id = str(ctx.author.id)
    ensure_user(user_id)
    user_data = stats[user_id]
    
    now = datetime.utcnow()
    if user_data["last_daily"]:
        last_daily = datetime.fromisoformat(user_data["last_daily"])
        if now - last_daily < timedelta(days=1):
            await ctx.send("You already claimed your daily reward. Come back later!")
            return
    
    user_data["money"] += 200
    user_data["last_daily"] = now.isoformat()
    save_stats()
    await ctx.send(f"{ctx.author.mention}, you received 200 dollars! You now have {user_data['money']} dollars.")

# gambling part 2
@bot.command()
async def blackjack(ctx, bet: int):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    user_id = str(ctx.author.id)
    ensure_user(user_id)
    user_data = stats[user_id]

    if bet <= 0:
        await ctx.send("Bet must be a positive number.")
        return
    if user_data["money"] < bet:
        await ctx.send("You don't have enough money to make this bet.")
        return

    def draw_card():
        cards = list(range(2, 11)) + ["J", "Q", "K", "A"]
        return random.choice(cards)

    def card_value(card):
        if card in ["J", "Q", "K"]:
            return 10
        elif card == "A":
            return 11  #lol
        return card

    def calculate_hand(hand):
        value = sum(card_value(c) for c in hand)
        num_aces = hand.count("A")
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    player_hand = [draw_card(), draw_card()]
    bot_hand = [draw_card(), draw_card()]

    while True:
        player_value = calculate_hand(player_hand)
        if player_value > 21:
            await ctx.send(f"You busted with {player_hand} (Value: {player_value}). You lose {bet} dollars!")
            user_data["money"] -= bet
            save_stats()
            return

        await ctx.send(f"Your hand: {player_hand} (Value: {player_value})\nBot shows: {bot_hand[0]}")
        await ctx.send("Type `hit` to draw another card or `stand` to hold.")
        
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == ctx.author and m.content.lower() in ["hit", "stand"])
        except:
            await ctx.send("You took too long! The bot wins by default.")
            user_data["money"] -= bet
            save_stats()
            return

        if msg.content.lower() == "hit":
            player_hand.append(draw_card())
        else:
            break

    bot_value = calculate_hand(bot_hand)
    while bot_value < 17:
        bot_hand.append(draw_card())
        bot_value = calculate_hand(bot_hand)

    player_value = calculate_hand(player_hand)
    if bot_value > 21 or player_value > bot_value:
        winnings = bet * 2
        user_data["money"] += winnings
        outcome = f"You win with {player_hand} (Value: {player_value}) vs Bot's {bot_hand} (Value: {bot_value})! You won {winnings} dollars!"
    elif player_value == bot_value:
        outcome = f"It's a tie! Your hand: {player_hand} (Value: {player_value}), Bot's hand: {bot_hand} (Value: {bot_value}). Your bet is returned."
    else:
        user_data["money"] -= bet
        outcome = f"You lose with {player_hand} (Value: {player_value}) vs Bot's {bot_hand} (Value: {bot_value}). You lost {bet} dollars."

    save_stats()
    await ctx.send(outcome)

# gambling part 3
@bot.command()
async def cointoss(ctx, bet: int, guess: str):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    user_id = str(ctx.author.id)
    ensure_user(user_id)
    user_data = stats[user_id]

    if bet <= 0:
        await ctx.send("Bet must be a positive number.")
        return
    if user_data["money"] < bet:
        await ctx.send("You don't have enough money to make this bet.")
        return
    if guess.lower() not in ["heads", "tails"]:
        await ctx.send("Your guess must be either 'heads' or 'tails'.")
        return

    result = random.choice(["heads", "tails"])
    if guess.lower() == result:
        winnings = bet * 2
        user_data["money"] += winnings
        outcome = f"The coin landed on {result}! You won {winnings} dollars!"
    else:
        user_data["money"] -= bet
        outcome = f"The coin landed on {result}. You lost {bet} dollars."

    save_stats()
    await ctx.send(outcome)

# leadeboard type shit - TODO: make this not ping the users in the leadeboard but i am lazy so i wont do it yourself
@bot.command()
async def leaderboard(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["money"], reverse=True)
    leaderboard_text = "\n".join(
        f"<@{user_id}>: {data['money']} dollars" for user_id, data in sorted_stats[:10]
    )
    await ctx.send(f"**Leaderboard:**\n{leaderboard_text}")

# gift money to the poor
@bot.command()
async def gift(ctx, recipient: discord.Member, amount: int):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    donor_id = str(ctx.author.id)
    recipient_id = str(recipient.id)
    ensure_user(donor_id)
    ensure_user(recipient_id)

    if amount <= 0:
        await ctx.send("The amount must be a positive number.")
        return
    if stats[donor_id]["money"] < amount:
        await ctx.send("You don't have enough money to gift.")
        return

    stats[donor_id]["money"] -= amount
    stats[recipient_id]["money"] += amount
    save_stats()
    await ctx.send(f"{ctx.author.mention} gifted {amount} dollars to {recipient.mention}!")

# gambling part 4 TODO: make this more interesting
@bot.command()
async def duel(ctx, opponent: discord.Member, bet: int):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("no")
        return

    challenger_id = str(ctx.author.id)
    opponent_id = str(opponent.id)
    ensure_user(challenger_id)
    ensure_user(opponent_id)

    if bet <= 0:
        await ctx.send("The bet must be a positive number.")
        return
    if stats[challenger_id]["money"] < bet or stats[opponent_id]["money"] < bet:
        await ctx.send("Both players must have enough money for the bet.")
        return

    def draw_card():
        cards = list(range(2, 11)) + ["J", "Q", "K", "A"]
        return random.choice(cards)

    def card_value(card):
        if card in ["J", "Q", "K"]:
            return 10
        elif card == "A":
            return 11
        return card

    def calculate_hand(hand):
        value = sum(card_value(c) for c in hand)
        num_aces = hand.count("A")
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    challenger_hand = [draw_card(), draw_card()]
    opponent_hand = [draw_card(), draw_card()]

    # challenger turn (the real man)
    while True:
        challenger_value = calculate_hand(challenger_hand)
        if challenger_value > 21:
            await ctx.send(f"{ctx.author.mention} busted with {challenger_hand} (Value: {challenger_value}). {opponent.mention} wins!")
            stats[opponent_id]["money"] += bet
            stats[challenger_id]["money"] -= bet
            save_stats()
            return

        await ctx.send(f"{ctx.author.mention}'s hand: {challenger_hand} (Value: {challenger_value})\n{opponent.mention} shows: {opponent_hand[0]}")
        await ctx.send(f"{ctx.author.mention}, type `hit` to draw another card or `stand` to hold.")
        
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == ctx.author and m.content.lower() in ["hit", "stand"])
        except:
            await ctx.send(f"{ctx.author.mention} took too long! {opponent.mention} wins by default!")
            stats[opponent_id]["money"] += bet
            stats[challenger_id]["money"] -= bet
            save_stats()
            return

        if msg.content.lower() == "hit":
            challenger_hand.append(draw_card())
        else:
            break

    # opponent turn (the gay one)
    opponent_value = calculate_hand(opponent_hand)
    while opponent_value < 17:
        opponent_hand.append(draw_card())
        opponent_value = calculate_hand(opponent_hand)

    # final comparison type bit
    if opponent_value > 21 or challenger_value > opponent_value:
        stats[challenger_id]["money"] += bet
        stats[opponent_id]["money"] -= bet
        outcome = f"{ctx.author.mention} wins with {challenger_hand} (Value: {challenger_value}) vs {opponent.mention}'s {opponent_hand} (Value: {opponent_value})! You won {bet} dollars!"
    elif challenger_value == opponent_value:
        outcome = f"It's a tie! {ctx.author.mention}'s hand: {challenger_hand} (Value: {challenger_value}), {opponent.mention}'s hand: {opponent_hand} (Value: {opponent_value}). Your bet is returned."
    else:
        stats[opponent_id]["money"] += bet
        stats[challenger_id]["money"] -= bet
        outcome = f"{opponent.mention} wins with {opponent_hand} (Value: {opponent_value}) vs {ctx.author.mention}'s {challenger_hand} (Value: {challenger_value})! You lost {bet} dollars."

    save_stats()
    await ctx.send(outcome)

# 
@bot.event
async def on_ready():
    print(f"[LOG] [SUCKAN1GGADICK]Logged in as {bot.user}")


bot.run("bot token here plewse :3")
  
