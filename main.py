import io
import json
import logging
import math
import os
import random
import re
import uuid
import textwrap
import matplotlib.pyplot as plt
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# ADMINS = ["smacksmackk", "titaniumbutter", "dufwha", "iblametruth"]

DROPS_FILE = "./data/drops.json"
EVENT_FILE = "./data/events.json"
EVENT_TYPES_FILE = "./data/event_types.json"
GAMES_FILE = "./data/games.json"
MEMBERS_FILE = "./data/members.json"
FREE_AGENTS_FILE = "./data/events_free_agents.json"
TEAMS_FILE = "./data/teams.json"
SCHEDULED_TASKS_FILE = './data/scheduled_tasks.json'

#--------------------------------------------------------------------------------------------------------------------------------------------
# Logging setup
#--------------------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(filename='bot_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MyClient(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def on_ready(self):
    self.load_data()
    await self.tree.sync()
    print('Logged on as', self.user)
    print('------')

  async def setup_hook(self) -> None:
        self.scheduled_tasks = self.load_scheduled_tasks()
        await self.tree.sync()
        self.execute_all_scheduled_tasks.start()

  def load_data(self):
    self.event_types = self.load_event_types()
    self.drops = self.load_drops()
    self.events = self.load_events()
    self.games = self.load_games()
    self.members = self.load_members()
    self.free_agents = self.load_free_agents()
    self.teams = self.load_teams()
    self.scheduled_tasks = self.load_scheduled_tasks()

  async def on_message(self, message):
    if message.author == client.user:
      return

    if message.content.startswith('!play'):
      return

    await client.process_commands(message)

  # Data Loading and Initialization
  def load_event_types(self):
    if os.path.exists(EVENT_TYPES_FILE):
      with open(EVENT_TYPES_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}
       
  def load_drops(self):
    if os.path.exists(DROPS_FILE):
      with open(DROPS_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_drops(self):
    with open(DROPS_FILE, 'w') as f:
      json.dump(self.drops, f, indent=2)


  def load_events(self):
    if os.path.exists(EVENT_FILE):
      with open(EVENT_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_events(self):
    with open(EVENT_FILE, 'w') as f:
      json.dump(self.events, f, indent=2)

  def load_games(self):
    if os.path.exists(GAMES_FILE):
      with open(GAMES_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_games(self):
    with open(GAMES_FILE, 'w') as f:
      json.dump(self.games, f, indent=2)

  def load_members(self):
    if os.path.exists(MEMBERS_FILE):
      with open(MEMBERS_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_members(self):
    with open(MEMBERS_FILE, 'w') as f:
      json.dump(self.members, f, indent=2)

  def load_free_agents(self):
    if os.path.exists(FREE_AGENTS_FILE):
      with open(FREE_AGENTS_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_free_agents(self):
    with open(FREE_AGENTS_FILE, 'w') as f:
      json.dump(self.free_agents, f, indent=2)

  def load_teams(self):
    if os.path.exists(TEAMS_FILE):
      with open(TEAMS_FILE, 'r') as f:
        return json.load(f)
    else:
      return {}

  def save_teams(self):
    with open(TEAMS_FILE, 'w') as f:
      json.dump(self.teams, f, indent=2)

  def load_scheduled_tasks(self):
    if os.path.exists(SCHEDULED_TASKS_FILE):
        with open(SCHEDULED_TASKS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"extravaganza_tasks": [], "bingo_tasks": [], "snakes_ladders_tasks": []}

  def save_scheduled_tasks(self, scheduled_tasks):
    with open(SCHEDULED_TASKS_FILE, 'w') as f:
      json.dump(scheduled_tasks, f, indent=2)

  @tasks.loop(minutes=60.0)
  async def execute_all_scheduled_tasks(self):
      scheduled_tasks = self.load_scheduled_tasks()

      # Extravaganza Tasks
      for game_uuid in scheduled_tasks.get("extravaganza_tasks", []):
          await self.execute_extravaganza_task(game_uuid)

      # Bingo Tasks
      for game_uuid in scheduled_tasks.get("bingo_tasks", []):
          await self.execute_bingo_task(game_uuid)

      # Snakes and Ladders Tasks
      for game_uuid in scheduled_tasks.get("snakes_ladders_tasks", []):
          await self.execute_snakes_ladders_task(game_uuid)

  async def execute_extravaganza_task(self, game_uuid):
    logging.info(f"Automatic extravaganza_tasks triggered. Game UUID: {game_uuid}")
    channel_leaderboard = self.get_channel(1349916162527461437)
    channel_graph = self.get_channel(1349916162527461437)

    if channel_leaderboard and channel_graph:
        # Announce Team Scores
        embeds = []
        if game_uuid and game_uuid in self.games:
            game_data = self.games[game_uuid]["game_data"]
            teams_data = game_data.get("teams", {})
            if teams_data:
                team_total_points = {team: data.get("total_points", 0) for team, data in teams_data.items()}
                sorted_teams = sorted(team_total_points.items(), key=lambda item: item[1], reverse=True)
                for team, points in sorted_teams:
                    points_display = int(points) if isinstance(points, (int, float)) and points.is_integer() else points
                    team_color = None
                    event_name = next((event_name for event_name, event_data in self.events.items() if event_data.get("game_id") == game_uuid), None)
                    if event_name and event_name in self.teams and team in self.teams[event_name]:
                        team_color_hex = self.teams[event_name][team]["color"]
                        team_color = discord.Color(int(team_color_hex.lstrip('#'), 16))
                    else:
                        team_color = discord.Color.default()
                    embed = discord.Embed(
                        description=f"**{team}:** {points_display} points",
                        color=team_color,
                    )
                    embeds.append(embed)
            if embeds:
                await channel_leaderboard.send(f"# {event_name} Leaderboard:", embeds=embeds)

        # Send Graph
        try:
            if game_uuid and game_uuid in self.games:
                game_data = self.games[game_uuid]["game_data"]
                teams_data = game_data.get("teams", {})
                if teams_data:
                    team_total_points = {team: data.get("total_points", 0) for team, data in teams_data.items()}
                    sorted_teams_points = sorted(team_total_points.items(), key=lambda item: item[1])
                    teams = [item[0] for item in sorted_teams_points]
                    points = [item[1] for item in sorted_teams_points]

                    plt.figure(figsize=(10, 6))

                    event_name = next((event_name for event_name, event_data in self.events.items() if event_data.get("game_id") == game_uuid), None)

                    if event_name and event_name in self.teams:
                        colors = [
                            tuple(c / 255 for c in discord.Color(int(self.teams[event_name][team]["color"].lstrip('#'), 16)).to_rgb())
                            for team in teams
                        ]
                        plt.barh(teams, points, color=colors)
                    else:
                        plt.barh(teams, points)

                    plt.xlabel("Total Points")
                    plt.title("Team Points Leaderboard")
                    plt.subplots_adjust(left=0.2)

                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)

                    file = discord.File(buffer, filename="leaderboard.png")
                    await channel_graph.send(file=file)
                    plt.close()
                else:
                    await channel_graph.send("No team drop counts available for this game.")
            else:
                await channel_graph.send(f"No game data found for UUID: {game_uuid}")
        except Exception as e:
            print(f"Error sending graph: {e}")
            await channel_graph.send(f"An error occurred while generating or sending the graph: {e}")

  @execute_all_scheduled_tasks.before_loop
  async def before_execute_all_scheduled_tasks(self):
      await self.wait_until_ready()

  # # Placeholder for Bingo Scheduled tasks (Add actual task logic here)
  # @tasks.loop(minutes=1.0)
  # async def bingo_tasks(self, game_uuid=None, force=False):
  #   now = datetime.datetime.now()
  #   if force or now.minute == 0:
  #     if game_uuid in self.scheduled_tasks.get("bingo_tasks", []) or force:
  #       logging.info(f"Bingo tasks triggered. Game UUID: {game_uuid}, Force: {force}")
  #       # Add bingo task logic here
  #       # ...
  #       if force:
  #         logging.info(f"Bingo tasks ran immediately for game UUID: {game_uuid}")

  # @bingo_tasks.before_loop
  # async def before_bingo_tasks(self):
  #   await self.wait_until_ready()

  # # Placeholder for Snakes and Ladders Scheduled tasks (Add actual task logic here)
  # @tasks.loop(minutes=1.0)
  # async def snakes_ladders_tasks(self, game_uuid=None, force=False):
  #   now = datetime.datetime.now()
  #   if force or now.minute == 0:
  #     if game_uuid in self.scheduled_tasks.get("snakes_ladders_tasks", []) or force:
  #       logging.info(f"Snakes and Ladders tasks triggered. Game UUID: {game_uuid}, Force: {force}")
  #       # Add snakes and ladders task logic here
  #       # ...
  #       if force:
  #         logging.info(f"Snakes and Ladders tasks ran immediately for game UUID: {game_uuid}")

  # @snakes_ladders_tasks.before_loop
  # async def before_snakes_ladders_tasks(self):
  #   await self.wait_until_ready()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyClient(command_prefix='!', intents=intents)
client.event_types = client.load_event_types()
client.drops = client.load_drops()
client.events = client.load_events()
client.games = client.load_games()
client.members = client.load_members()
client.free_agents = client.load_free_agents()
client.teams = client.load_teams()

#--------------------------------------------------------------------------------------------------------------------------------------------
# General functions
#--------------------------------------------------------------------------------------------------------------------------------------------

async def generate_snakes_ladders_board(board_size, num_snakes, num_ladders, tasks_file="./data/snakes_and_ladders_tasks.json"):
    """Generates a random snakes and ladders board with tasks populated, strictly limiting to 25 tasks per difficulty range."""
    board = [None] * (board_size * board_size)  # Initialize board with None
    snakes = []
    ladders = []
    positions = list(range(1, board_size * board_size - 1))  # Exclude 0 and the last square

    # Generate snakes
    for _ in range(num_snakes):
        if len(positions) < 2:
            break  # Not enough positions for a snake
        head, tail = random.sample(positions, 2)
        if head > tail:
            snakes.append((head, tail))
            positions.remove(head)
            positions.remove(tail)

    # Generate ladders
    for _ in range(num_ladders):
        if len(positions) < 2:
            break  # Not enough positions for a ladder
        bottom, top = random.sample(positions, 2)
        if bottom < top:
            ladders.append((bottom, top))
            positions.remove(bottom)
            positions.remove(top)

    # Load tasks from JSON and sort by difficulty
    try:
        with open(tasks_file, "r") as f:
            tasks_data = json.load(f)
            if isinstance(tasks_data, list):
                tasks = tasks_data
            else:
                tasks = tasks_data.get("tasks", [])

        # Sort tasks by difficulty: Easy, Medium, Hard, Expert
        difficulty_order = {"Easy": 0, "Medium": 1, "Hard": 2, "Expert": 3}
        tasks.sort(key=lambda task: difficulty_order.get(task.get("difficulty", "Medium")))  # Default to Medium if no difficulty

    except FileNotFoundError:
        print(f"Error: Tasks file '{tasks_file}' not found.")
        return board, snakes, ladders

    used_positions = set()  # Keep track of positions already used.

    # Distribute tasks based on difficulty, strictly limiting to 25 per range
    task_index = 0
    difficulty_ranges = {
        "Easy": (1, board_size * board_size // 4),
        "Medium": (board_size * board_size // 4, 2 * board_size * board_size // 4),
        "Hard": (2 * board_size * board_size // 4, 3 * board_size * board_size // 4),
        "Expert": (3 * board_size * board_size // 4, board_size * board_size - 1)
    }

    difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0, "Expert": 0}

    # Place easy tasks
    available_positions = [pos for pos in range(difficulty_ranges["Easy"][0], difficulty_ranges["Easy"][1]) if pos not in used_positions and pos not in [head for head, tail in snakes] and pos not in [bottom for bottom, top in ladders]]
    random.shuffle(available_positions)
    while task_index < len(tasks) and difficulty_counts["Easy"] < 25 and available_positions:
        if tasks[task_index]["difficulty"] == "Easy":
            position = available_positions.pop(0)
            board[position] = tasks[task_index]["task"]
            used_positions.add(position)
            difficulty_counts["Easy"] += 1
            task_index += 1
        else:
            task_index += 1

    # Place medium tasks
    available_positions = [pos for pos in range(difficulty_ranges["Medium"][0], difficulty_ranges["Medium"][1]) if pos not in used_positions and pos not in [head for head, tail in snakes] and pos not in [bottom for bottom, top in ladders]]
    random.shuffle(available_positions)
    while task_index < len(tasks) and difficulty_counts["Medium"] < 25 and available_positions:
        if tasks[task_index]["difficulty"] == "Medium":
            position = available_positions.pop(0)
            board[position] = tasks[task_index]["task"]
            used_positions.add(position)
            difficulty_counts["Medium"] += 1
            task_index += 1
        else:
            task_index += 1

    # Place hard tasks
    available_positions = [pos for pos in range(difficulty_ranges["Hard"][0], difficulty_ranges["Hard"][1]) if pos not in used_positions and pos not in [head for head, tail in snakes] and pos not in [bottom for bottom, top in ladders]]
    random.shuffle(available_positions)
    while task_index < len(tasks) and difficulty_counts["Hard"] < 25 and available_positions:
        if tasks[task_index]["difficulty"] == "Hard":
            position = available_positions.pop(0)
            board[position] = tasks[task_index]["task"]
            used_positions.add(position)
            difficulty_counts["Hard"] += 1
            task_index += 1
        else:
            task_index += 1

    # Place expert tasks in remaining slots
    available_positions = [pos for pos in range(difficulty_ranges["Expert"][0], difficulty_ranges["Expert"][1]) if pos not in used_positions and pos not in [head for head, tail in snakes] and pos not in [bottom for bottom, top in ladders]]
    random.shuffle(available_positions)
    while task_index < len(tasks) and available_positions:
        if tasks[task_index]["difficulty"] == "Expert":
            position = available_positions.pop(0)
            board[position] = tasks[task_index]["task"]
            used_positions.add(position)
            task_index += 1
        else:
            task_index += 1

    # Add tasks to snake tails and ladder tops
    for head, tail in snakes:
        if board[tail] is None:
            if task_index < len(tasks):
                board[tail] = tasks[task_index]["task"]
                task_index += 1
    for bottom, top in ladders:
        if board[top] is None:
            if task_index < len(tasks):
                board[top] = tasks[task_index]["task"]
                task_index += 1

    # Add start and finish
    board[0] = "Start"
    board[board_size * board_size - 1] = "Finish"

    return board, snakes, ladders

def generate_bingo_board(board_size, drops_data):
  """Generates a bingo board with random boss names and images from drops_data, with center 'Recruit A New Member'."""
  boss_data = {boss: data for boss, data in drops_data.items() if "(" not in boss}  # Filter bosses with parentheses
  boss_names = list(boss_data.keys())
  board = []
  selected_bosses = random.sample(boss_names, board_size * board_size - 1)  # -1 to account for center

  center_index = board_size * board_size // 2  # Find the center.

  for i in range(board_size):
    row = []
    for j in range(board_size):
      index = i * board_size + j
      if index == center_index:
        row.append({"name": "Recruit A New Member", "image": "./bingo/assets/images/recruit.png"})  # Placeholder image
      elif index > center_index:
        boss_name = selected_bosses[index - 1]  # Adjust for the removed spot.
        row.append({"name": boss_name, "image": boss_data[boss_name]["image"]})
      else:
        boss_name = selected_bosses[index]
        row.append({"name": boss_name, "image": boss_data[boss_name]["image"]})
    board.append(row)

  return board

async def regenerate_gameboard(event_name, client):
  """Regenerates the gameboard for snakes_ladders and bingo events."""
  if event_name not in client.events:
    return "Event does not exist."

  game_id = client.events[event_name]["game_id"]
  if game_id not in client.games:
    return "Game data not found."

  event_type = client.events[event_name]["type"]
  game_data = {}

  if event_type == "snakes_ladders":
    board_size = 10
    num_snakes = 8
    num_ladders = 8
    board, snakes, ladders = await generate_snakes_ladders_board(board_size, num_snakes, num_ladders)
    game_data["board"] = board
    game_data["snakes"] = snakes
    game_data["ladders"] = ladders

    if "teams" in client.games[game_id]:
      for team_id in client.games[game_id]["teams"]:
        client.games[game_id]["teams"][team_id]["position"] = 0

  elif event_type == "bingo":
    board_size = 5
    game_data["board"] = generate_bingo_board(board_size, client.drops)

  elif event_type == "extravaganza":
    return "Extravaganza gameboards cannot be regenerated."

  else:
    return "Regeneration is not supported for this event type."

  client.games[game_id]["game_data"] = game_data
  client.save_games()

  return f"Gameboard for {event_name} regenerated."


async def draw_snakes_ladders_board_image(board, snakes, ladders, pawns):
  """Draws Snakes and Ladders with task text and text-based pawn pieces."""
  board_size = len(board)
  grid_size = int(board_size**0.5)
  cell_size = 110
  image_size = cell_size * grid_size + 2

  img = Image.new("RGBA", (image_size, image_size), (43, 43, 43, 255))
  draw = ImageDraw.Draw(img)
  number_font = ImageFont.truetype("arialbd.ttf", 14)
  font_size = 10
  font = ImageFont.truetype("arialbd.ttf", font_size)
  bold_font = ImageFont.truetype("arialbd.ttf", 24)

  # Adjust snakes and ladders to 0-based indexing
  snakes = [(start, end) for start, end in snakes]
  ladders = [(start, end) for start, end in ladders]

  # Draw board cells and highlight snake/ladder starts/ends
  for row in range(grid_size):
    for col in range(grid_size):
      cell_x1 = col * cell_size
      cell_y1 = row * cell_size
      cell_x2 = cell_x1 + cell_size
      cell_y2 = cell_y1 + cell_size

      cell_number = grid_size * (grid_size - 1 - row) + (col if row % 2 == 0 else grid_size - 1 - col)

      # Default cell color
      cell_color = (43, 43, 43, 255)  # background color

      is_snake_or_ladder_end = False

      # Highlight snake start/end
      for start, end in snakes:
        if cell_number == start or cell_number == end:
          cell_color = (244, 204, 204, 255)  # light red
          is_snake_or_ladder_end = True
          break

      # Highlight ladder start/end
      for start, end in ladders:
        if cell_number == start or cell_number == end:
          cell_color = (207, 226, 243, 255)  # light blue
          is_snake_or_ladder_end = True
          break

      draw.rectangle([(cell_x1, cell_y1), (cell_x2, cell_y2)], fill=cell_color, outline="black", width=2)

      # Draw cell numbers
      number_width = draw.textbbox((0, 0), str(cell_number + 1), font=number_font)[2] - draw.textbbox((0, 0), str(cell_number + 1), font=number_font)[0]
      draw.text((col * cell_size + cell_size - number_width - 5, row * cell_size + 5), str(cell_number + 1), fill="gray", font=number_font)

      # Draw cell text
      if board[cell_number]:
        text = str(board[cell_number])
        wrapped_text = textwrap.wrap(text, width=18)
        if text == "Start" or text == "Finish":
          text_width = draw.textbbox((0, 0), text, font=bold_font)[2] - draw.textbbox((0, 0), text, font=bold_font)[0]
          text_height = draw.textbbox((0, 0), text, font=bold_font)[3] - draw.textbbox((0, 0), text, font=bold_font)[1]
          draw.text((cell_x1 + cell_size / 2 - text_width / 2, cell_y1 + cell_size / 2 - text_height / 2), text, fill="white", font=bold_font)
        else:
          y_offset = 15
          for line in wrapped_text:
            draw.text((col * cell_size + 5, row * cell_size + y_offset), line, fill=("white" if not is_snake_or_ladder_end else "black"), font=font)
            y_offset += font.getbbox(line)[3] - font.getbbox(line)[1] + 2

  for start, end in snakes:
    start_row = grid_size - 1 - start // grid_size
    start_col = start % grid_size if start_row % 2 == 0 else grid_size - 1 - start % grid_size
    end_row = grid_size - 1 - end // grid_size
    end_col = end % grid_size if end_row % 2 == 0 else grid_size - 1 - end % grid_size

    start_x = start_col * cell_size + cell_size // 2
    start_y = start_row * cell_size + cell_size // 2
    end_x = end_col * cell_size + cell_size // 2
    end_y = end_row * cell_size + cell_size // 2

    green_color = (0, 128, 0, int(255 * 0.8))  # Green with 0.8 opacity

    # Calculate wiggle points (smoke wave)
    num_segments = 50  # More segments for smoother curves
    points = []
    for i in range(num_segments + 1):
      t = i / num_segments
      x = start_x + (end_x - start_x) * t
      y = start_y + (end_y - start_y) * t
      amplitude = 10 * t
      frequency = 5 + 3 * t
      wiggle = amplitude * math.sin(frequency * t * math.pi * 2)
      points.append((x, y + wiggle))

    # Draw snake head (bigger and round)
    head_x, head_y = points[0]
    head_radius = 5  # Define head_radius here

    # Determine snake direction from head (start) to next segment
    direction_x = points[1][0] - points[0][0]
    direction_y = points[1][1] - points[0][1]

    # Calculate angle of the snake's head
    angle = math.atan2(direction_y, direction_x)

    # Draw snake tongue (small wiggly red)
    tongue_length = 10
    tongue_width = 2
    tongue_wiggle = 2

    # Adjust angle to make the tongue point out from the head
    angle += math.pi  # Add 180 degrees (pi radians) to make it point opposite the head

    tongue_x1 = points[0][0] + head_radius * math.cos(angle)
    tongue_y1 = points[0][1] + head_radius * math.sin(angle)

    tongue_x2 = tongue_x1 + tongue_length * math.cos(angle)
    tongue_y2 = tongue_y1 + tongue_length * math.sin(angle) + random.randint(-tongue_wiggle, tongue_wiggle)

    tongue_x3 = tongue_x2 + tongue_length // 2 * math.cos(angle)
    tongue_y3 = tongue_y2 + tongue_length // 2 * math.sin(angle) + random.randint(-tongue_wiggle, tongue_wiggle)

    # Create a separate transparent layer for the snake
    snake_layer = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
    snake_draw = ImageDraw.Draw(snake_layer)

    # Draw the snake with varying thickness
    num_segments = len(points) - 1
    for i in range(num_segments):
      x1, y1 = points[i]
      x2, y2 = points[i + 1]
      thickness = int(15 - 13 * (i / num_segments))
      snake_draw.line([(x1, y1), (x2, y2)], fill=green_color, width=thickness)

    snake_draw.ellipse((head_x - head_radius, head_y - head_radius, head_x + head_radius, head_y + head_radius), fill=green_color)

    # Draw snake eye (black dot)
    eye_radius = 2
    eye_x = head_x + head_radius // 2
    eye_y = head_y - head_radius // 3
    snake_draw.ellipse((eye_x - eye_radius, eye_y - eye_radius, eye_x + eye_radius, eye_y + eye_radius), fill="black")

    snake_draw.line([(tongue_x1, tongue_y1), (tongue_x2, tongue_y2), (tongue_x3, tongue_y3)], fill="red", width=tongue_width)

    img.paste(snake_layer, (0, 0), snake_layer)

  for start, end in ladders:
    start_row = grid_size - 1 - start // grid_size
    start_col = start % grid_size if start_row % 2 == 0 else grid_size - 1 - start % grid_size
    end_row = grid_size - 1 - end // grid_size
    end_col = end % grid_size if end_row % 2 == 0 else grid_size - 1 - end % grid_size

    start_x = start_col * cell_size + cell_size // 2
    start_y = start_row * cell_size + cell_size // 2
    end_x = end_col * cell_size + cell_size // 2
    end_y = end_row * cell_size + cell_size // 2

    ladder_width = 15
    brown_color = (137, 81, 41, 200)

    ladder_layer = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
    ladder_draw = ImageDraw.Draw(ladder_layer)

    if start_row == end_row:  # Horizontal ladder
      ladder_draw.line([(start_x, start_y - ladder_width), (end_x, end_y - ladder_width)], fill=brown_color, width=5)
      ladder_draw.line([(start_x, start_y + ladder_width), (end_x, end_y + ladder_width)], fill=brown_color, width=5)

      num_rungs = 15
      for i in range(num_rungs):
        rung_x = start_x + (end_x - start_x) * (i + 1) / (num_rungs + 1)
        ladder_draw.line([(rung_x, start_y - ladder_width), (rung_x, start_y + ladder_width)], fill=brown_color, width=3)
    else:  # Vertical or diagonal ladder
      ladder_draw.line([(start_x - ladder_width, start_y), (end_x - ladder_width, end_y)], fill=brown_color, width=5)
      ladder_draw.line([(start_x + ladder_width, start_y), (end_x + ladder_width, end_y)], fill=brown_color, width=5)

      num_rungs = 15
      for i in range(num_rungs):
        rung_x1 = start_x - ladder_width + (end_x - start_x) * (i + 1) / (num_rungs + 1)
        rung_y1 = start_y + (end_y - start_y) * (i + 1) / (num_rungs + 1)
        rung_x2 = start_x + ladder_width + (end_x - start_x) * (i + 1) / (num_rungs + 1)
        rung_y2 = start_y + (end_y - start_y) * (i + 1) / (num_rungs + 1)
        ladder_draw.line([(rung_x1, rung_y1), (rung_x2, rung_y2)], fill=brown_color, width=3)

    img.paste(ladder_layer, (0, 0), ladder_layer)

#   for i in range(board_size):
#     row = grid_size - 1 - i // grid_size
#     col = i % grid_size if row % 2 == 0 else grid_size - 1 - i % grid_size
#     x = col * cell_size + cell_size // 2
#     y = row * cell_size + cell_size // 2
#     if board[i]:
#       text = str(board[i])
#       wrapped_text = textwrap.wrap(text, width=18)
#       if text == "Start" or text == "Finish":
#         text_width = draw.textbbox((0, 0), text, font=bold_font)[2] - draw.textbbox((0, 0), text, font=bold_font)[0]
#         text_height = draw.textbbox((0, 0), text, font=bold_font)[3] - draw.textbbox((0, 0), text, font=bold_font)[1]
#         draw.text((x - text_width / 2, y - text_height / 2), text, fill="white", font=bold_font)
#       else:
#         y_offset = 15
#         for line in wrapped_text:
#           draw.text((col * cell_size + 5, row * cell_size + y_offset), line, fill="white", font=font)
#           y_offset += font.getbbox(line)[3] - font.getbbox(line)[1] + 2

  # Group pawns by position
  pawns_by_position = {}
  for pawn in pawns:
    position = pawn["position"]
    if position not in pawns_by_position:
      pawns_by_position[position] = []
    pawns_by_position[position].append(pawn)

  # Draw pawns
  for position, pawns_at_position in pawns_by_position.items():
    row = grid_size - 1 - position // grid_size
    col = position % grid_size if row % 2 == 0 else grid_size - 1 - position % grid_size
    x = col * cell_size + cell_size // 2
    y = row * cell_size + cell_size // 2

    num_pawns = len(pawns_at_position)
    pawn_size = cell_size // 4
    pawn_spacing = pawn_size // 2  # Adjust spacing as needed

    # Calculate starting position for pawns based on their number
    start_x = x - (num_pawns - 1) * pawn_spacing / 2

    for i, pawn in enumerate(pawns_at_position):
      pawn_x = start_x + i * pawn_spacing
      pawn_y = y - pawn_size

      # Draw a simplified pawn
      pawn_color = pawn.get("color", (245, 245, 220))  # Light beige as default
      pawn_outline = pawn.get("outline", "black")

      # Draw the body (triangle)
      triangle_points = [
        (pawn_x + pawn_size / 2, pawn_y + pawn_size * 0.25),
        (pawn_x, pawn_y + pawn_size * 1.75),
        (pawn_x + pawn_size, pawn_y + pawn_size * 1.75)
      ]
      draw.polygon(triangle_points, fill=pawn_color, outline=pawn_outline, width=2)

      # Draw the head (circle)
      draw.ellipse((pawn_x, pawn_y, pawn_x + pawn_size, pawn_y + pawn_size), fill=pawn_color, outline=pawn_outline, width=2)

  buffer = io.BytesIO()
  img.save(buffer, format="PNG")
  buffer.seek(0)
  file = discord.File(buffer, filename="snakes_ladders_board.png")
  return file

async def draw_bingo_board_image(board):
  cell_size = 150
  board_size = len(board)
  border_width = 3
  padding = 10
  image_size = cell_size * board_size + border_width * (board_size + 1) + 2 * padding

  img = Image.new("RGBA", (image_size, image_size), (43, 43, 43, 255))
  draw = ImageDraw.Draw(img)

  for i in range(board_size + 1):
    line_y = i * (cell_size + border_width) + padding
    draw.line([(padding, line_y), (image_size - padding, line_y)], fill="black", width=border_width)
    line_x = i * (cell_size + border_width) + padding
    draw.line([(line_x, padding), (line_x, image_size - padding)], fill="black", width=border_width)

  for row_index, row in enumerate(board):
    for col_index, cell in enumerate(row):
      x0 = col_index * (cell_size + border_width) + border_width + padding
      y0 = row_index * (cell_size + border_width) + border_width + padding

      if cell["image"]:
        try:
          cell_img = Image.open(cell["image"]).resize((cell_size - 10, cell_size - 50))
          cell_img = cell_img.convert("RGBA")
          img_x = x0 + (cell_size - cell_img.width) // 2
          img_y = y0 + (cell_size - cell_img.height) // 2
          img.paste(cell_img, (img_x, img_y), cell_img)
        except FileNotFoundError:
          logging.error(f"Image not found: {cell['image']}")
        except Exception as e:
          logging.error(f"Error loading image: {e}")
          logging.error(f"Image mode: {cell_img.mode}")

      font_boss = ImageFont.truetype("arialbd.ttf", 20)
      max_line_width = cell_size - 10
      wrapped_text = []
      words = cell["name"].split()
      current_line = ""
      for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox_test = draw.textbbox((0, 0), test_line, font=font_boss)
        if bbox_test[2] - bbox_test[0] <= max_line_width:
          current_line = test_line
        else:
          wrapped_text.append(current_line)
          current_line = word
      wrapped_text.append(current_line)

      y_offset = 0
      line_spacing = 10
      total_text_height = sum([draw.textbbox((0, 0), line, font=font_boss)[3] - draw.textbbox((0, 0), line, font=font_boss)[1] for line in wrapped_text]) + (len(wrapped_text) - 1) * line_spacing

      start_y = y0 + (cell_size - total_text_height) // 2

      for line in wrapped_text:
        bbox_boss = draw.textbbox((0, 0), line, font=font_boss)
        text_width_boss = bbox_boss[2] - bbox_boss[0]
        text_height_boss = bbox_boss[3] - bbox_boss[1]
        text_x_boss = x0 + (cell_size - text_width_boss) // 2
        text_y_boss = start_y + y_offset
        draw.text((text_x_boss, text_y_boss), line, fill="white", font=font_boss)
        y_offset += text_height_boss + line_spacing

  buffer = io.BytesIO()
  img.save(buffer, format="PNG")
  buffer.seek(0)
  file = discord.File(buffer, filename="bingo_board.png")
  return file

async def draw_bingo_text_image(cell_size, board_size, border_width, padding):
  bingo_letters = "BINGO"
  font = ImageFont.truetype("arialbd.ttf", cell_size)
  font_outline = ImageFont.truetype("arialbd.ttf", cell_size + 2)

  total_width = board_size * (150 + border_width) + 2 * padding #Use 150 for the column width
  max_height = cell_size + 10

  img = Image.new("RGBA", (total_width, max_height), (43, 43, 43, 255))
  draw = ImageDraw.Draw(img)

  for i, letter in enumerate(bingo_letters):
    column_center = i * (150 + border_width) + 75 + padding #use 150 for column center
    letter_width = draw.textbbox((0, 0), letter, font=font)[2] - draw.textbbox((0, 0), letter, font=font)[0]
    x = column_center - letter_width // 2
    y = 0

    draw.text((x - 1, y - 1), letter, fill="black", font=font_outline)
    draw.text((x + 1, y - 1), letter, fill="black", font=font_outline)
    draw.text((x - 1, y + 1), letter, fill="black", font=font_outline)
    draw.text((x + 1, y + 1), letter, fill="black", font=font_outline)
    draw.text((x, y), letter, fill="white", font=font)

  buffer = io.BytesIO()
  img.save(buffer, format="PNG")
  buffer.seek(0)
  file = discord.File(buffer, filename="bingo_text.png")
  return file

async def draw_and_send_board(interaction, game_data, teams):
    """Draws and sends the Snakes and Ladders board."""
    board = game_data["board"]
    snakes = game_data["snakes"]
    ladders = game_data["ladders"]

    pawns = []
    for team_name, team_data in teams.items():
        team_color = team_data.get("color", (245, 245, 220))
        pawn_position = game_data.get("pawns", {}).get(team_name, [0])[-1] #get the latest position

        pawns.append({
            "name": team_name,
            "position": pawn_position,
            "color": team_color,
            "outline": "black"
        })

    image = await draw_snakes_ladders_board_image(board, snakes, ladders, pawns)

    if image:
        await interaction.followup.send(file=image)
    else:
        await interaction.followup.send("Failed to generate the Snakes and Ladders board image. Please check the image folders.", ephemeral=True)

def process_drop_data(event_name: str, team_name: str, member_id: str, osrs_ign: str, boss_name: str, drop_name: str):
    """Processes a boss drop and returns the message string, original points, added points, and new total points."""

    boss_drops = client.drops
    events_data = client.events
    games_data = client.games

    if boss_name not in boss_drops:
        return f"❌ Boss '{boss_name}' not found.", 0, 0, 0

    drops = boss_drops[boss_name]["drops"]
    if drop_name not in drops:
        return f"❌ Drop '{drop_name}' not found for {boss_name}.", 0, 0, 0

    point_value = drops[drop_name]

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return f"❌ Game ID '{game_id}' not found in games.json.", 0, 0, 0

    game_data = games_data[game_id]["game_data"]
    teams_data = game_data.setdefault("teams", {})
    team_data = teams_data.setdefault(team_name, {"total_points": 0, "drops": {}})
    boss_data = team_data["drops"].setdefault(boss_name, {})
    drop_data = boss_data.setdefault(drop_name, {"count": 0, "points": []})

    original_points = team_data["total_points"]

    drop_count = drop_data["count"]
    if (boss_name == "Barrows Chests" or boss_name == "Moons of Peril") and drop_count >= 4:
        point_value /= 2
        point_value_display = int(point_value) if point_value.is_integer() else point_value
        message_addition = f"Congratulations on a 5th drop! **{drop_name}** from **{boss_name}** is worth **{point_value_display} points** since it is a 5th drop! Added to {team_name} gotten by **{osrs_ign}**."
    elif not (boss_name == "Barrows Chests" or boss_name == "Moons of Peril") and drop_count >= 1:
        point_value /= 2
        point_value_display = int(point_value) if point_value.is_integer() else point_value
        message_addition = f"Congratulations on a duplicate drop! **{drop_name}** from **{boss_name}** is worth **{point_value_display} points** since it is a duplicate! Added to {team_name} gotten by **{osrs_ign}**."
    else:
        message_addition = f"🗡️ **{drop_name}** from **{boss_name}** is worth **{point_value} points**! Added to **{team_name}** gotten by **{osrs_ign}**."

    drop_data["count"] += 1
    drop_data["points"].append({member_id: point_value}) # Modified line

    team_data["total_points"] += point_value

    client.save_games()

    return message_addition, original_points, point_value, team_data["total_points"]

def process_drop_removal(event_name: str, team_name: str, member_id: str, osrs_ign: str, boss_name: str, drop_name: str):
    """Processes a boss drop removal and returns the message string, original points, removed points, and new total points."""

    boss_drops = client.drops
    events_data = client.events
    games_data = client.games

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return f"❌ Game ID '{game_id}' not found in games.json.", 0, 0, 0

    game_data = games_data[game_id]["game_data"]
    teams_data = game_data["teams"]
    team_data = teams_data.get(team_name, {"total_points": 0, "drops": {}})
    boss_data = team_data["drops"].get(boss_name, {})
    drop_data = boss_data.get(drop_name, {"count": 0, "points": []})

    if drop_data["count"] > 0:
        if boss_name in boss_drops and drop_name in boss_drops[boss_name]["drops"]:
            point_value = boss_drops[boss_name]["drops"][drop_name]
        else:
            return f"❌ Point value not found for {drop_name} at {boss_name}.", 0, 0, 0

        if (boss_name == "Barrows Chests" or boss_name == "Moons of Peril") and drop_data["count"] > 4:
            point_value /= 2
        elif drop_data["count"] > 1:
            point_value /= 2

        member_points = []
        for point_entry in drop_data["points"]:
            if member_id in point_entry:
                member_points.append(point_entry)

        if not member_points:
            return f"❌ No {drop_name} found for {boss_name} from {osrs_ign}.", 0, 0, 0

        point_entry_to_remove = min(member_points, key=lambda x: x[member_id])
        removed_points = point_entry_to_remove[member_id]

        original_points = team_data["total_points"]

        team_data["total_points"] -= removed_points
        drop_data["count"] -= 1

        drop_data["points"].remove(point_entry_to_remove)

        if drop_data["count"] == 0:
            del boss_data[drop_name]
            if not boss_data:
                del team_data["drops"][boss_name]
                if not team_data["drops"]:
                    del teams_data[team_name]

        client.save_games()

        message_removal = f"Removed 1 **{drop_name}** from **{boss_name}** gotten by **{osrs_ign}**."

        return message_removal, original_points, removed_points, team_data["total_points"]
    else:
        return f"❌ No {drop_name} found for {boss_name} to remove for {team_name} in {event_name}.", 0, 0, 0


#--------------------------------------------------------------------------------------------------------------------------------------------
# Autocomplete functions for slash commands
#--------------------------------------------------------------------------------------------------------------------------------------------

async def event_type_autocomplete(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  suggestions = [
    app_commands.Choice(name=event_type, value=event_type)
    for event_type in client.event_types.keys()
    if current.lower() in event_type.lower()
  ]
  return suggestions[:25]

async def event_name_autocomplete(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  suggestions = [
    app_commands.Choice(name=event_name, value=event_name)
    for event_name in client.events.keys()
    if current.lower() in event_name.lower()
  ]
  return suggestions[:25]

async def event_names_in_events_free_agents_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    event_names = [
        name for name, agents in client.free_agents.items() if agents  # Only include if not empty
    ]
    return [
        app_commands.Choice(name=name, value=name)
        for name in event_names
        if current.lower() in name.lower()
    ]

async def event_names_with_teams_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    event_names = [
        name for name, teams in client.teams.items() if teams  # Only include if there are teams
    ]
    return [
        app_commands.Choice(name=name, value=name)
        for name in event_names
        if current.lower() in name.lower()
    ]

async def event_name_user_in_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    member_name = interaction.user.name
    suggestions = []

    if not hasattr(interaction.client, 'free_agents'):
        return []

    if member_name not in interaction.client.members:
        return []

    for event_name, free_agents in interaction.client.free_agents.items():
        if any(agent["discord_user"] == member_name for agent in free_agents) and current.lower() in event_name.lower():
            suggestions.append(app_commands.Choice(name=event_name, value=event_name))

    return suggestions[:25]

async def event_name_user_not_in_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    member_name = interaction.user.name
    suggestions = []

    if member_name not in interaction.client.members:
        return []

    for event_name in interaction.client.events:
        # Check free agents
        if hasattr(interaction.client, 'free_agents') and event_name in interaction.client.free_agents:
            if any(agent["discord_user"] == member_name for agent in interaction.client.free_agents[event_name]):
                continue  # User is already a free agent for this event

        # Check teams
        if hasattr(interaction.client, 'teams') and event_name in interaction.client.teams:
            for team in interaction.client.teams[event_name].values():
                if any(member["discord_user"] == member_name for member in team["members"]):
                    continue  # User is already in a team for this event

        # If user is not in free agents or teams, add to suggestions
        if current.lower() in event_name.lower():
            suggestions.append(app_commands.Choice(name=event_name, value=event_name))

    return suggestions[:25]

async def selected_character_autocomplete(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  event_name = interaction.namespace.event_name
  if interaction.user.name in client.members:
    suggestions = [
      app_commands.Choice(name=ign, value=ign)
      for ign in client.members[interaction.user.name]["osrs_igns"]
      if current.lower() in ign.lower()
    ]
    return suggestions[:25]
  return []

async def teams_in_event_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name

    if event_name and event_name in client.teams:
        team_names = list(client.teams[event_name].keys())
        return [
            app_commands.Choice(name=name, value=name)
            for name in team_names if current.lower() in name.lower()
        ][:25]
    return []

async def team_event_autocomplete_all(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    suggestions = []
    if hasattr(interaction.client, "teams") and isinstance(interaction.client.teams, dict):
        for event_name in interaction.client.teams:
            if current.lower() in event_name.lower():
                suggestions.append(app_commands.Choice(name=event_name, value=event_name))
    return suggestions[:25]  

async def team_member_ign_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    suggestions = []
    if hasattr(interaction.client, "teams") and isinstance(interaction.client.teams, dict):
        for event_teams in interaction.client.teams.values():
            if isinstance(event_teams, dict):
                for team in event_teams.values():
                    if isinstance(team, dict) and "members" in team:
                        for member in team["members"]:
                            if current.lower() in member["osrs_ign"].lower():
                                suggestions.append(app_commands.Choice(name=member["osrs_ign"], value=member["osrs_ign"]))
    return suggestions[:25]

async def team_event_autocomplete_for_member_ign(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    member_ign = interaction.namespace.member_ign
    suggestions = []
    if not hasattr(interaction.client, "teams"):
        return []

    for event_name, event_teams in interaction.client.teams.items():
        if isinstance(event_teams, dict):
            for team in event_teams.values():
                if isinstance(team, dict) and "members" in team:
                    if any(member["osrs_ign"] == member_ign for member in team["members"]) and current.lower() in event_name.lower():
                        suggestions.append(app_commands.Choice(name=event_name, value=event_name))
    return suggestions[:25]

async def team_role_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    member_ign = interaction.namespace.member_ign
    event_name = interaction.namespace.event_name
    suggestions = []

    if not hasattr(interaction.client, "teams") or event_name not in interaction.client.teams:
        return []

    for team in interaction.client.teams[event_name].values():
        for member in team["members"]:
            if member["osrs_ign"] == member_ign:
                if member["role"] == "member" and current.lower() in "leader":
                    suggestions.append(app_commands.Choice(name="leader", value="leader"))
                elif member["role"] == "leader" and current.lower() in "member":
                    suggestions.append(app_commands.Choice(name="member", value="member"))
                return suggestions
    return suggestions

async def admin_team_member_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name
    team_name = interaction.namespace.team_name

    if event_name and team_name and event_name in client.teams and team_name in client.teams[event_name]:
        return [
            app_commands.Choice(name=member["osrs_ign"], value=member["discord_user"])
            for member in client.teams[event_name][team_name]["members"]
            if current.lower() in member["osrs_ign"].lower()
        ][:25]
    return []

async def team_member_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name
    member_id = str(interaction.user.name)
    teams = client.teams

    if event_name not in teams:
        return []

    team_found = None
    for team, team_details in teams[event_name].items():
        for member in team_details["members"]:
            if member["discord_user"] == member_id:
                team_found = team
                break
        if team_found:
            break

    if not team_found:
        return []

    return [
        app_commands.Choice(name=member["osrs_ign"], value=member["discord_user"])
        for member in client.teams[event_name][team_found]["members"]
        if current.lower() in member["osrs_ign"].lower()
    ][:25]

async def admin_drop_remove_member_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name
    team_name = interaction.namespace.team_name
    games_data = client.games
    events_data = client.events

    if not event_name or not team_name:
        return []

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or team_name not in game_data["teams"]:
        return []

    team_data = game_data["teams"][team_name]
    member_ids = set()

    if "drops" in team_data:
        for boss in team_data["drops"].values():
            for drops in boss.values():
                for point_entry in drops["points"]:
                    member_ids.update(point_entry.keys())

    members = []
    if event_name in client.teams and team_name in client.teams[event_name]:
        for member in client.teams[event_name][team_name]["members"]:
            if member["discord_user"] in member_ids:
                members.append(member)

    return [
        app_commands.Choice(name=member["osrs_ign"], value=member["discord_user"])
        for member in members if current.lower() in member["osrs_ign"].lower()
    ][:25]

async def drop_remove_member_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name
    member_id = str(interaction.user.name)
    games_data = client.games
    events_data = client.events
    teams = client.teams

    if event_name not in teams:
        return []

    team_name = None
    for team, team_details in teams[event_name].items():
        for member in team_details["members"]:
            if member["discord_user"] == member_id:
                team_name = team
                break
        if team_name:
            break

    if not team_name:
        return []

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or team_name not in game_data["teams"]:
        return []

    team_data = game_data["teams"][team_name]
    member_ids = set()

    if "drops" in team_data:
        for boss in team_data["drops"].values():
            for drops in boss.values():
                for point_entry in drops["points"]:
                    member_ids.update(point_entry.keys())

    members = []
    if event_name in client.teams and team_name in client.teams[event_name]:
        for member in client.teams[event_name][team_name]["members"]:
            if member["discord_user"] in member_ids:
                members.append(member)

    return [
        app_commands.Choice(name=member["osrs_ign"], value=member["discord_user"])
        for member in members if current.lower() in member["osrs_ign"].lower()
    ][:25]

async def free_agent_autocomplete(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  event_name = interaction.namespace.event_name
  if event_name in client.free_agents:
    suggestions = [
      app_commands.Choice(name=free_agent["osrs_ign"], value=free_agent["osrs_ign"])
      for free_agent in client.free_agents[event_name]
      if current.lower() in free_agent["osrs_ign"].lower()
    ]
    return suggestions[:25]
  return []

async def member_autocomplete_not_in_event(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name

    # Check if the event exists in members.json
    if not hasattr(interaction.client, 'members') or not interaction.client.members:
        return []  # Return empty if members data is not loaded

    # Check if the event exists in free agents
    if not hasattr(interaction.client, 'free_agents') or event_name not in interaction.client.free_agents:
        free_agents_in_event = []
    else:
        free_agents_in_event = [agent["discord_user"] for agent in interaction.client.free_agents[event_name]]

    # Check if the event exists in teams
    if not hasattr(interaction.client, 'teams') or event_name not in interaction.client.teams:
        teams_in_event = {}
    else:
        teams_in_event = interaction.client.teams[event_name]

    members_in_teams = []
    for team in teams_in_event.values():
        for member in team["members"]:
            members_in_teams.append(member["discord_user"])

    suggestions = []
    for member_name in interaction.client.members:
        if (
            member_name not in free_agents_in_event
            and member_name not in members_in_teams
            and current.lower() in member_name.lower()
        ):
            suggestions.append(app_commands.Choice(name=member_name, value=member_name))

    return suggestions[:25]

async def selected_character_autocomplete_member(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  member_name = interaction.namespace.member_name
  if member_name in client.members:
    suggestions = [
      app_commands.Choice(name=ign, value=ign)
      for ign in client.members[member_name]["osrs_igns"]
      if current.lower() in ign.lower()
    ]
    return suggestions[:25]
  return []

async def member_autocomplete_in_event_free_agents(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name

    if not hasattr(interaction.client, 'free_agents') or event_name not in interaction.client.free_agents:
        return []

    free_agents = interaction.client.free_agents[event_name]
    suggestions = [
        app_commands.Choice(name=agent["osrs_ign"], value=agent["osrs_ign"])
        for agent in free_agents
        if current.lower() in agent["osrs_ign"].lower()
    ]
    return suggestions[:25]

async def bingo_snakes_event_autocomplete(
  interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
  suggestions = []
  for event_name, event_data in client.events.items():
    if event_data["type"] in ["bingo", "snakes_ladders"] and current.lower() in event_name.lower():
      suggestions.append(app_commands.Choice(name=event_name, value=event_name))
  return suggestions[:25]

async def snakes_ladders_event_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    suggestions = []
    for event_name, event_data in client.events.items():
        if event_data["type"] == "snakes_ladders" and current.lower() in event_name.lower():
            suggestions.append(app_commands.Choice(name=event_name, value=event_name))
    return suggestions[:25]  # Limit to 25 choices

async def extravaganza_event_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_names = list(client.events.keys())
    return [
        app_commands.Choice(name=name, value=name)
        for name in event_names if current.lower() in name.lower() and client.events[name]["type"] == "extravaganza"
    ][:25]

async def teams_with_drops_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    event_name = interaction.namespace.event_name
    games_data = client.games
    events_data = client.events

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data:
        return []

    team_names_with_drops = list(game_data["teams"].keys())

    return [
        app_commands.Choice(name=name, value=name)
        for name in team_names_with_drops if current.lower() in name.lower()
    ][:25]

async def boss_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    boss_names = list(client.drops.keys())
    return [
        app_commands.Choice(name=name, value=name)
        for name in boss_names if current.lower() in name.lower()
    ][:25]

async def drop_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    boss_name = interaction.namespace.boss_name  # Retrieve the boss_name from the interaction namespace
    if boss_name and boss_name in client.drops:
        drop_names = list(client.drops[boss_name]["drops"].keys())
        return [
            app_commands.Choice(name=name, value=name)
            for name in drop_names if current.lower() in name.lower()
        ][:25]
    return []

async def admin_team_boss_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    teams = client.teams
    events_data = client.events
    games_data = client.games

    event_name = interaction.namespace.event_name
    team_name = interaction.namespace.team_name
    member_id = interaction.namespace.team_member_name

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    if event_name not in teams:
        return []

    if team_name not in teams[event_name]:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or team_name not in game_data["teams"]:
        return []

    team_data = game_data["teams"][team_name]
    boss_names = []

    if "drops" in team_data:
        for boss_name, drops in team_data["drops"].items():
            for drop_name, drop_data in drops.items():
                for point_entry in drop_data["points"]:
                    if member_id in point_entry:
                        boss_names.append(boss_name)
                        break
                else:
                    continue
                break
    boss_names = list(set(boss_names)) #remove duplicates.

    return [
        app_commands.Choice(name=name, value=name)
        for name in boss_names if current.lower() in name.lower()
    ][:25]

async def admin_team_drop_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    teams = client.teams
    events_data = client.events
    games_data = client.games

    event_name = interaction.namespace.event_name
    team_name = interaction.namespace.team_name  # Get team_name from namespace
    boss_name = interaction.namespace.boss_name

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    if event_name not in teams:
        return []

    if team_name not in teams[event_name]: #check if the team exists in the event.
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or team_name not in game_data["teams"]:
        return []

    if boss_name not in game_data["teams"][team_name]["drops"]:
        return []

    drop_names = list(game_data["teams"][team_name]["drops"][boss_name].keys())

    return [
        app_commands.Choice(name=name, value=name)
        for name in drop_names if current.lower() in name.lower()
    ][:25]

async def team_boss_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    member_id = str(interaction.user.name)
    teams = client.teams
    events_data = client.events
    games_data = client.games

    event_name = interaction.namespace.event_name
    team_member_name = interaction.namespace.team_member_name

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    if event_name not in teams:
        return []

    user_team = None
    for team_name, team_details in teams[event_name].items():
        for member in team_details["members"]:
            if member["discord_user"] == member_id and member["role"] == "leader":
                user_team = team_name
                break
        if user_team:
            break

    if not user_team:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or user_team not in game_data["teams"]:
        return []

    team_data = game_data["teams"][user_team]
    boss_names = []

    if "drops" in team_data:
        for boss_name, drops in team_data["drops"].items():
            for drop_name, drop_data in drops.items():
                for point_entry in drop_data["points"]:
                    if team_member_name in point_entry:
                        boss_names.append(boss_name)
                        break
                else:
                    continue
                break
    boss_names = list(set(boss_names)) #remove duplicates.

    return [
        app_commands.Choice(name=name, value=name)
        for name in boss_names if current.lower() in name.lower()
    ][:25]

async def team_drop_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    member_id = str(interaction.user.name)
    teams = client.teams
    events_data = client.events
    games_data = client.games

    event_name = interaction.namespace.event_name
    boss_name = interaction.namespace.boss_name

    if event_name not in events_data:
        return []

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return []

    if event_name not in teams:
        return []

    user_team = None
    for team_name, team_details in teams[event_name].items():
        for member in team_details["members"]:
            if member["discord_user"] == member_id and member["role"] == "leader":
                user_team = team_name
                break
        if user_team:
            break

    if not user_team:
        return []

    game_data = games_data[game_id]["game_data"]
    if "teams" not in game_data or user_team not in game_data["teams"]:
        return []

    if boss_name not in game_data["teams"][user_team]["drops"]:
        return []

    drop_names = list(game_data["teams"][user_team]["drops"][boss_name].keys())

    return [
        app_commands.Choice(name=name, value=name)
        for name in drop_names if current.lower() in name.lower()
    ][:25]

async def scheduled_task_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:

    extravaganza_tasks = client.scheduled_tasks.get("extravaganza_tasks", [])

    choices = []
    for event_name, event_data in client.events.items():
        if event_data.get("game_id") in extravaganza_tasks:
            if current.lower() in event_name.lower(): # only show event names that include the current input
                choices.append(app_commands.Choice(name=event_name, value=event_name))

    return choices[:25]  # Discord API limit is 25 choices


#--------------------------------------------------------------------------------------------------------------------------------------------
# Admin commands
#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_event_create", description="Admin: Create a new event.")
@app_commands.describe(
  event_name="The name of the event (make it unique).",
  event_type="The type of the event.",
  event_date="The date of the event (MM/DD/YYYY).",
  event_time="The time of the event (12-hour format, HH:MM AM/PM CST).",
)
@app_commands.autocomplete(event_type=event_type_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_event_create(interaction: discord.Interaction, event_name: str, event_type: str, event_date: str, event_time: str):
  logging.info(f"Admin {interaction.user.name} used /admin_event_create to create {event_name} type {event_type} with starting date on {event_date} at {event_time}.")

  if event_name in client.events:
    await interaction.response.send_message("Event already exists.", ephemeral=True)
    return

  try:
    # Parse the date in MM/DD/YYYY format
    datetime.strptime(event_date, "%m/%d/%Y")
  except ValueError:
    await interaction.response.send_message("Invalid date format. Please use MM/DD/YYYY.", ephemeral=True)
    return

  game_uuid = str(uuid.uuid4())

  game_data = {}

  if event_type == "snakes_ladders":
    board_size = 10
    num_snakes = 8
    num_ladders = 8
    board, snakes, ladders = await generate_snakes_ladders_board(board_size, num_snakes, num_ladders)
    game_data["board"] = board
    game_data["snakes"] = snakes
    game_data["ladders"] = ladders

  elif event_type == "bingo":
    # Create a bingo board with boss names
    board_size = 5
    game_data["board"] = generate_bingo_board(board_size, client.drops)

  elif event_type == "extravaganza":
    game_data["teams"] = {}

  client.games[game_uuid] = {"game_data": game_data}  # Create the game object in games.json
  client.save_games()

  client.events[event_name] = {
    "type": event_type,
    "start_date": event_date,
    "start_time": event_time,
    "game_id": game_uuid  # Store only the UUID in events.json
  }
  client.save_events()

  await interaction.response.send_message(f"Event {event_name} created with type {event_type} on {event_date} at {event_time} with game id {game_uuid}.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_event_delete", description="Admin: Delete an existing event.")
@app_commands.describe(
  event_name="The name of the event to delete."
)
@app_commands.autocomplete(event_name=event_name_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_event_delete(interaction: discord.Interaction, event_name: str):
  logging.info(f"Admin {interaction.user.name} used /admin_event_delete to delete {event_name}.")

  if event_name not in client.events:
    await interaction.response.send_message("Event does not exist.", ephemeral=True)
    return

  event_data = client.events[event_name]
  game_uuid = event_data["game_id"]

  if game_uuid in client.games:
    del client.games[game_uuid]
    client.save_games()

  del client.events[event_name]
  client.save_events()

  # Remove teams associated with the event
  if event_name in client.teams:
    del client.teams[event_name]
    client.save_teams()

  # Remove free agents associated with the event
  if event_name in client.free_agents:
    del client.free_agents[event_name]
    client.save_free_agents()

  await interaction.response.send_message(f"Event {event_name} and associated game data, teams, and free agents deleted.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_regenerate_board", description="Admin: Regenerate the game board for an event.")
@app_commands.describe(event_name="The name of the event.")
@app_commands.autocomplete(event_name=event_name_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_regenerate_board(interaction: discord.Interaction, event_name: str):
  logging.info(f"Admin {interaction.user.name} used /admin_regenerate_board to regenerate the game board for {event_name}.")

  confirm_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="✅ Yes, Regenerate Board")
  cancel_button = discord.ui.Button(style=discord.ButtonStyle.secondary, label="❌ Cancel")

  async def confirm_callback(interaction_button: discord.Interaction):
    if interaction_button.user == interaction.user:
      result = await regenerate_gameboard(event_name, client)
      await interaction_button.response.send_message(result, ephemeral=True)
      await interaction.edit_original_response(view=None) #remove buttons
    else:
      await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

  async def cancel_callback(interaction_button: discord.Interaction):
    if interaction_button.user == interaction.user:
      await interaction_button.response.send_message("Board regeneration cancelled.", ephemeral=True)
      await interaction.edit_original_response(view=None) #remove buttons
    else:
      await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

  confirm_button.callback = confirm_callback
  cancel_button.callback = cancel_callback

  view = discord.ui.View()
  view.add_item(confirm_button)
  view.add_item(cancel_button)

  await interaction.response.send_message(f"Are you sure you want to regenerate the game board for {event_name}?", view=view, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_member_join", description="Admin: Add OSRS names for a user.")
@app_commands.describe(
  discord_user="The Discord user to add OSRS names for.",
  osrs_igns="The user's Old School RuneScape in-game names (comma-separated).",
)
@app_commands.default_permissions(administrator=True)
async def admin_member_join(
  interaction: discord.Interaction, discord_user: discord.Member, osrs_igns: str
):
  logging.info(f"Admin {interaction.user.name} used /admin_member_join to add OSRS names for {discord_user.name}.")
  
  if discord_user.name in client.members:
    await interaction.response.send_message(
      f"{discord_user.name} has already registered their OSRS names. Use /admin_member_update instead.",
      ephemeral=True,
    )
    return

  igns = [ign.strip() for ign in osrs_igns.split(",")]
  user_data = {"discord_user": discord_user.name, "osrs_igns": igns}

  client.members[discord_user.name] = user_data
  client.save_members()

  await interaction.response.send_message(
    f"OSRS names for {discord_user.name} have been saved: {', '.join(igns)}.",
    ephemeral=True,
  )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_member_update", description="Admin: Update OSRS names for a user.")
@app_commands.describe(
    discord_user="The Discord user to update OSRS names for.",
    osrs_igns="The user's Old School RuneScape in-game names (comma-separated).",
)
@app_commands.default_permissions(administrator=True)
async def admin_member_update(
    interaction: discord.Interaction, discord_user: discord.Member, osrs_igns: str
):
    logging.info(f"Admin {interaction.user.name} used /admin_member_update to update OSRS names for {discord_user.name}.")

    if discord_user.name not in client.members:
        await interaction.response.send_message(
            f"{discord_user.name} has not registered their OSRS names yet. Use /admin_member_join instead.",
            ephemeral=True,
        )
        return

    igns = [ign.strip() for ign in osrs_igns.split(",")]
    client.members[discord_user.name]["osrs_igns"] = igns
    client.save_members()

    await interaction.response.send_message(
        f"OSRS names for {discord_user.name} have been updated: {', '.join(igns)}.",
        ephemeral=True,
    )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_members_view", description="Admin: View all members and their OSRS names.")
@app_commands.default_permissions(administrator=True)
async def admin_members_view(interaction: discord.Interaction):
    logging.info(f"Admin {interaction.user.name} used /admin_members_view.")

    if not client.members:
        await interaction.response.send_message("No members data found.", ephemeral=True)
        return

    embed = discord.Embed(title="Members and OSRS IGNs", color=discord.Color.blue())

    for discord_user, data in client.members.items():
        osrs_igns_str = ", ".join(data['osrs_igns'])
        embed.add_field(name=discord_user, value=osrs_igns_str, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_event_join", description="Admin: Join a user to an event as a free agent.")
@app_commands.describe(
  event_name="The name of the event.",
  member_name="The Discord user to join.",
  selected_character="The character to use for this event.",
)
@app_commands.autocomplete(
  event_name=event_name_autocomplete,
  member_name=member_autocomplete_not_in_event,
  selected_character=selected_character_autocomplete_member,
)
@app_commands.default_permissions(administrator=True)
async def admin_member_event_join(
  interaction: discord.Interaction,
  event_name: str,
  member_name: str,
  selected_character: str,
):
  logging.info(f"Admin {interaction.user.name} used /admin_event_join to add {member_name} to {event_name} as a free agent with character '{selected_character}'.")

  if event_name not in client.events:
    await interaction.response.send_message("Event does not exist.", ephemeral=True)
    return

  if member_name not in client.members:
    await interaction.response.send_message(
      f"{member_name} has not registered their OSRS names. Use /admin_join first.",
      ephemeral=True,
    )
    return

  if selected_character not in client.members[member_name]["osrs_igns"]:
    await interaction.response.send_message("Invalid character selected.", ephemeral=True)
    return

  user_data = {"discord_user": member_name, "osrs_ign": selected_character}

  if event_name not in client.free_agents:
    client.free_agents[event_name] = []

  if user_data not in client.free_agents[event_name]:
    client.free_agents[event_name].append(user_data)
    client.save_free_agents()
    await interaction.response.send_message(
      f"{member_name} has joined {event_name} as a free agent with character '{selected_character}'.",
      ephemeral=True,
    )
  else:
    await interaction.response.send_message(
      f"{member_name} is already a free agent for {event_name}.",
      ephemeral=True,
    )

#--------------------------------------------------------------------------------------------------------------------------------------------


@client.tree.command(name="admin_event_unjoin", description="Admin: Remove a user from an event's free agent pool.")
@app_commands.describe(event_name="The name of the event.", member_osrs_ign="The OSRS username to remove.",)
@app_commands.autocomplete(event_name=event_name_autocomplete, member_osrs_ign=member_autocomplete_in_event_free_agents)
@app_commands.default_permissions(administrator=True)
async def admin_event_unjoin(interaction: discord.Interaction, event_name: str, member_osrs_ign: str):
    logging.info(f"Admin {interaction.user.name} used /admin_event_unjoin to remove {member_osrs_ign} from {event_name}.")

    if event_name not in client.events:
        await interaction.response.send_message("Event does not exist.", ephemeral=True)
        return

    if event_name in client.free_agents:
        free_agents = client.free_agents[event_name]
        users_to_remove = [agent for agent in free_agents if agent["osrs_ign"] == member_osrs_ign]

        if users_to_remove:
            for user_data in users_to_remove:
                free_agents.remove(user_data)
            client.save_free_agents()
            await interaction.response.send_message(
                f"{member_osrs_ign} has been removed from {event_name}'s free agent pool.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"{member_osrs_ign} is not a free agent for {event_name}.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            f"{member_osrs_ign} is not a free agent for {event_name}.",
            ephemeral=True,
        )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_team_create", description="Admin: Create a new team for an event.")
@app_commands.describe(
  event_name="The name of the event.",
  team_name="The name of the team.",
  team_color="The color of the team (e.g. '#FF0000').",
)
@app_commands.autocomplete(event_name=event_name_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_team_create(interaction: discord.Interaction, event_name: str, team_name: str, team_color: str):
  logging.info(f"Admin {interaction.user.name} used /admin_team_create to create team {team_name} for {event_name} with color {team_color}.")

  if event_name not in client.events:
    await interaction.response.send_message("Event does not exist.", ephemeral=True)
    return

  if team_name in client.teams.get(event_name, {}):
    await interaction.response.send_message("Team name already exists for this event.", ephemeral=True)
    return

  if event_name not in client.teams:
    client.teams[event_name] = {}

  if not re.match(r'^#[0-9a-fA-F]{6}$', team_color):
    await interaction.response.send_message("Invalid color code. Please use a 6-character hex code (e.g., '#FF0000').", ephemeral=True)
    return

  client.teams[event_name][team_name] = {
    "color": team_color,
    "members": []
  }
  client.save_teams()

  # Add pawn position if event is snakes_ladders
  if client.events[event_name]["type"] == "snakes_ladders":
      game_uuid = client.events[event_name]["game_id"]
      if game_uuid in client.games:
          game_data = client.games[game_uuid]["game_data"]
          if "pawns" not in game_data:
              game_data["pawns"] = {}  # Initialize pawns if not present
          if team_name not in game_data["pawns"]:
              game_data["pawns"][team_name] = 0  # Add pawn with initial position 0
              client.save_games() # Save changes to the game object.

  embed = discord.Embed(
    title=f"Team '{team_name}' Created!",
    description=f"Team '{team_name}' created for {event_name}.",
    color=int(team_color[1:], 16)  # Convert hex to int for embed color
  )
  embed.add_field(name="Team Color", value=team_color, inline=False)
  await interaction.response.send_message(embed=embed, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_team_delete", description="Admin: Delete a team from an event.")
@app_commands.describe(
    event_name="The name of the event.",
    team_name="The name of the team to delete.",
)
@app_commands.autocomplete(event_name=event_name_autocomplete, team_name=teams_in_event_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_team_delete(interaction: discord.Interaction, event_name: str, team_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_team_delete to delete team {team_name} from {event_name}.")

    if event_name not in client.events:
        await interaction.response.send_message("Event does not exist.", ephemeral=True)
        return

    if event_name not in client.teams or team_name not in client.teams[event_name]:
        await interaction.response.send_message("Team does not exist for this event.", ephemeral=True)
        return

    # Fetch existing free agents for the event
    existing_free_agents = client.free_agents.get(event_name, []).copy()

    # Move members to free agents
    if "members" in client.teams[event_name][team_name]:
        for member in client.teams[event_name][team_name]["members"]:
            if "role" in member:
                del member["role"]

            # Check if a member with the same discord_user and osrs_ign exists
            exists = False
            for existing_member in existing_free_agents:
                if existing_member["discord_user"] == member["discord_user"] and existing_member["osrs_ign"] == member["osrs_ign"]:
                    exists = True
                    break

            if not exists:
                existing_free_agents.append(member)

        # Save the updated free agents list for the event
        client.free_agents[event_name] = existing_free_agents
        client.save_free_agents()

    del client.teams[event_name][team_name]
    client.save_teams()

    # Remove team data from games.json
    game_uuid = client.events[event_name]["game_id"]
    if game_uuid in client.games:
        game_data = client.games[game_uuid]["game_data"]
        if "teams" in game_data and team_name in game_data["teams"]:
            del game_data["teams"][team_name]
            client.save_games()

    # Remove pawn position if event is snakes_ladders
    if client.events[event_name]["type"] == "snakes_ladders":
        if game_uuid in client.games:
            game_data = client.games[game_uuid]["game_data"]
            if "pawns" in game_data and team_name in game_data["pawns"]:
                del game_data["pawns"][team_name]
                client.save_games()

    embed = discord.Embed(
        title=f"Team '{team_name}' Deleted!",
        description=f"Team '{team_name}' deleted from {event_name}. Members moved to free agents.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_team_role_change", description="Admin: Change the role of a member in a team.")
@app_commands.describe(
    event_name="The event the user is in.",
    member_ign="The OSRS IGN to change the role of.",
    new_role="The new role (leader or member).",
)
@app_commands.autocomplete(
    event_name=team_event_autocomplete_all,
    member_ign=team_member_ign_autocomplete,
    new_role=team_role_autocomplete,
)
@app_commands.default_permissions(administrator=True)
async def admin_team_role_change(
    interaction: discord.Interaction,
    event_name: str,
    member_ign: str,
    new_role: str,
):
    logging.info(f"Admin {interaction.user.name} used /admin_team_role_change to change {member_ign}'s role in {event_name} to {new_role}.")

    if event_name not in client.teams:
        await interaction.response.send_message("Invalid event name.", ephemeral=True)
        return

    event_teams = client.teams[event_name]
    member_found = False

    for team in event_teams.values():
        for member in team["members"]:
            if member["osrs_ign"] == member_ign:
                member["role"] = new_role
                member_found = True
                break
        if member_found:
            break

    if not member_found:
        await interaction.response.send_message("Member not found in any team for this event.", ephemeral=True)
        return

    client.save_teams()
    await interaction.response.send_message(f"{member_ign}'s role in {event_name} changed to {new_role}.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_boss_drops_showall", description="Admin: Shows all boss drops and points in embeds.")
@app_commands.default_permissions(administrator=True)
async def boss_drops_all(interaction: discord.Interaction):
    logging.info(f"Admin {interaction.user.name} used /admin_boss_drops_showall")

    embeds_and_files = []

    for boss_name, boss_data in client.drops.items():
        embed = discord.Embed(title=f"{boss_name}", color=discord.Color.blurple())
        drops = boss_data.get("drops", {})
        image_path = boss_data.get("image")

        file = None
        if image_path and os.path.exists(image_path):
            file = discord.File(image_path, filename=os.path.basename(image_path))
            embed.set_thumbnail(url=f"attachment://{os.path.basename(image_path)}")

        for drop_name, points in drops.items():
            embed.add_field(name=drop_name, value=f"Points: {points}", inline=False)
            if len(embed.fields) >= 25:
                embed.add_field(name="Warning", value=f"Too many drops for {boss_name}. Some drops may not be shown.", inline=False)
                break

        embeds_and_files.append((embed, file))

    if not embeds_and_files:
        return await interaction.response.send_message("No boss drops found.", ephemeral=True)

    # Send embeds in batches of 10
    for i in range(0, len(embeds_and_files), 10):
        batch = embeds_and_files[i:i + 10]
        embeds = []
        files = []

        for embed_data, file in batch:
            embeds.append(embed_data)
            if file and os.path.exists(file.fp.name):  # Ensure the file exists before adding
                files.append(discord.File(file.fp.name, filename=file.filename))

        if i == 0:
            await interaction.response.send_message(embeds=embeds, files=files)
        else:
            await interaction.followup.send(embeds=embeds, files=files)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_boss_drop_edit", description="Admin: Edit boss drop points.")
@app_commands.describe(boss_name="The name of the boss.", drop_name="The name of the drop.", points="The new point value.")
@app_commands.autocomplete(boss_name=boss_autocomplete, drop_name=drop_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_boss_drop_edit(interaction: discord.Interaction, boss_name: str, drop_name: str, points: int):
    logging.info(f"Admin {interaction.user.name} used /admin_boss_drop_edit to edit {boss_name} {drop_name} to {points} points.")

    if boss_name not in client.drops:
        await interaction.response.send_message("Boss does not exist.", ephemeral=True)
        return

    if "drops" not in client.drops[boss_name]:
        await interaction.response.send_message("This boss has no drops defined.", ephemeral=True)
        return

    if drop_name not in client.drops[boss_name]["drops"]:
        await interaction.response.send_message("Drop does not exist for this boss.", ephemeral=True)
        return

    previous_points = client.drops[boss_name]["drops"][drop_name]
    client.drops[boss_name]["drops"][drop_name] = points
    client.save_drops()

    await interaction.response.send_message(
        f"Updated {drop_name} for {boss_name} from {previous_points} to {points} points.",
        ephemeral=True,
    )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_boss_drop_add", description="Admin: Add a new boss drop.")
@app_commands.describe(boss_name="The name of the boss.", drop_name="The name of the drop.", points="The point value.")
@app_commands.autocomplete(boss_name=boss_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_boss_drop_add(interaction: discord.Interaction, boss_name: str, drop_name: str, points: int):
    logging.info(f"Admin {interaction.user.name} used /admin_boss_drop_add to add {drop_name} to {boss_name} with {points} points.")

    if boss_name not in client.drops:
        await interaction.response.send_message("Boss does not exist.", ephemeral=True)
        return

    if "drops" not in client.drops[boss_name]:
        client.drops[boss_name]["drops"] = {}

    if drop_name in client.drops[boss_name]["drops"]:
        previous_points = client.drops[boss_name]["drops"][drop_name]
        client.drops[boss_name]["drops"][drop_name] = points
        client.save_drops()
        await interaction.response.send_message(
            f"Updated {drop_name} for {boss_name} from {previous_points} to {points} points.",
            ephemeral=True,
        )
    else:
        client.drops[boss_name]["drops"][drop_name] = points
        client.save_drops()
        await interaction.response.send_message(
            f"Added {drop_name} to {boss_name} with {points} points.",
            ephemeral=True,
        )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_boss_drop_remove", description="Admin: Remove a boss drop.")
@app_commands.describe(boss_name="The name of the boss.", drop_name="The name of the drop.")
@app_commands.autocomplete(boss_name=boss_autocomplete, drop_name=drop_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_boss_drop_remove(interaction: discord.Interaction, boss_name: str, drop_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_boss_drop_remove to remove {drop_name} from {boss_name}.")

    if boss_name not in client.drops:
        await interaction.response.send_message("Boss does not exist.", ephemeral=True)
        return

    if "drops" not in client.drops[boss_name] or drop_name not in client.drops[boss_name]["drops"]:
        await interaction.response.send_message("Drop does not exist for this boss.", ephemeral=True)
        return

    confirm_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="✅ Yes, Remove Drop")
    cancel_button = discord.ui.Button(style=discord.ButtonStyle.secondary, label="❌ Cancel")

    async def confirm_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            del client.drops[boss_name]["drops"][drop_name]
            client.save_drops()
            await interaction_button.response.send_message(f"Removed {drop_name} from {boss_name}.", ephemeral=True)
            await interaction.edit_original_response(view=None)  # remove buttons
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    async def cancel_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            await interaction_button.response.send_message("Drop removal cancelled.", ephemeral=True)
            await interaction.edit_original_response(view=None)  # remove buttons
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(f"Are you sure you want to remove {drop_name} from {boss_name}?", view=view, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_extravaganza_drop", description="Admin: Help a member add a drop to their team.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_name=teams_in_event_autocomplete, team_member_name=admin_team_member_autocomplete, boss_name=boss_autocomplete, drop_name=drop_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_extravaganza_drop(interaction: discord.Interaction, event_name: str, team_name: str, team_member_name: str, boss_name: str, drop_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_extravaganza_drop to help {team_member_name} in {team_name} in {event_name} add a drop {drop_name} for {boss_name}.")

    if event_name not in client.teams:
        return await interaction.response.send_message(f"❌ Event '{event_name}' not found.", ephemeral=True)

    if team_name not in client.teams[event_name]:
        return await interaction.response.send_message(f"❌ Team '{team_name}' not found in event '{event_name}'.", ephemeral=True)

    if client.events[event_name]["type"] != "extravaganza":
        return await interaction.response.send_message(f"❌ Event '{event_name}' is not an extravaganza event.", ephemeral=True)

    for member in client.teams[event_name][team_name]["members"]:
        if member["discord_user"] == team_member_name:
            osrs_ign = member["osrs_ign"]
            break
    else:
        return await interaction.response.send_message(f"❌ Member '{team_member_name}' not found in team '{team_name}'.", ephemeral=True)

    message, original_points, added_points, new_total_points = process_drop_data(event_name, team_name, team_member_name, osrs_ign, boss_name, drop_name)

    if message.startswith("❌"):
        return await interaction.response.send_message(message, ephemeral=True)

    team_color = client.teams[event_name][team_name]["color"]
    team_color_discord = discord.Color(int(team_color.lstrip('#'), 16))
    embed = discord.Embed(
        description=f"{message}\n"
                    f"**Original points**: {int(original_points)}\n"
                    f"**Added points**: {int(added_points)}\n"
                    f"**New total points**: {int(new_total_points)}",
        color=team_color_discord
    )
    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_extravaganza_drop_remove", description="Admin: Remove a drop from a team.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_name=teams_with_drops_autocomplete, team_member_name=admin_drop_remove_member_autocomplete, boss_name=admin_team_boss_autocomplete, drop_name=admin_team_drop_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_extravaganza_drop_remove(interaction: discord.Interaction, event_name: str, team_name: str, team_member_name: str, boss_name: str, drop_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_extravaganza_drop_remove to remove drop {drop_name} for {boss_name} gotten by {team_member_name} in {event_name} from {team_name}.")

    # Get the osrs_ign from the selected discord user.
    for member in client.teams[event_name][team_name]["members"]:
        if member["discord_user"] == team_member_name:
            osrs_ign = member["osrs_ign"]
            break
    else:
        return await interaction.response.send_message(f"❌ Member '{team_member_name}' not found in team '{team_name}'.", ephemeral=True)

    message, original_points, removed_points, new_total_points = process_drop_removal(event_name, team_name, team_member_name, osrs_ign, boss_name, drop_name)

    if message.startswith("❌"):
        return await interaction.response.send_message(message, ephemeral=True)

    team_color = client.teams[event_name][team_name]["color"]
    team_color_discord = discord.Color(int(team_color.lstrip('#'), 16))
    embed = discord.Embed(
        title=f"🗑️ {team_name} - {event_name}",
        description=f"{message}\n"
                    f"**Original points**: {int(original_points)}\n"
                    f"**Points removed**: {int(removed_points)}\n"
                    f"**New total points**: {int(new_total_points)}",
        color=team_color_discord
    )
    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_extravaganza_plyr_drops_rm", description="Admin: Remove all drops for a specific player.")
@app_commands.describe(event_name="The name of the event.", team_name="The name of the team.", team_member_name="The Discord name of the player.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_name=teams_in_event_autocomplete, team_member_name=team_member_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_extravaganza_plyr_drops_rm(interaction: discord.Interaction, event_name: str, team_name: str, team_member_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_extravaganza_plyr_drops_rm to remove drops for {team_member_name} in {team_name} in {event_name}.")

    if event_name not in client.teams or team_name not in client.teams[event_name]:
        await interaction.response.send_message("Event or team not found.", ephemeral=True)
        return

    team_data = client.teams[event_name][team_name]
    player_found = False
    osrs_ign = None

    for member in team_data["members"]:
        if member["discord_user"] == team_member_name:
            player_found = True
            osrs_ign = member["osrs_ign"]
            break

    if not player_found:
        await interaction.response.send_message("Player not found in team.", ephemeral=True)
        return

    game_uuid = None
    for event, event_data in client.events.items():
        if event == event_name:
            game_uuid = event_data.get("game_id")
            break

    if not game_uuid:
        await interaction.response.send_message("Game data for event not found.", ephemeral=True)
        return

    game_data = client.games.get(game_uuid, {}).get("game_data", {})
    teams_data = game_data.get("teams", {})

    if team_name not in teams_data or "drops" not in teams_data[team_name]:
        await interaction.response.send_message("No drops found for the team.", ephemeral=True)
        return

    team_drops = teams_data[team_name]["drops"]
    removed_points = 0
    drops_removed = 0
    removed_drops_list = []

    for boss, drops in list(team_drops.items()):
        for drop, drop_data in list(drops.items()):
            points_list = drop_data.get("points", [])
            new_points_list = []
            for point_entry in points_list:
                if team_member_name not in point_entry:
                    new_points_list.append(point_entry)
                else:
                    removed_points += point_entry[team_member_name]
                    drops_removed += 1
                    removed_drops_list.append(f"{drop} from {boss} ({point_entry[team_member_name]} points)")

            team_drops[boss][drop]["points"] = new_points_list
            team_drops[boss][drop]["count"] = len(new_points_list)

            if not team_drops[boss][drop]["points"]:
                del team_drops[boss][drop]
        if not team_drops[boss]:
            del team_drops[boss]

    teams_data[team_name]["total_points"] -= removed_points
    teams_data["total_points"] -= removed_points
    new_team_total_points = teams_data[team_name]["total_points"]

    client.games[game_uuid]["game_data"]["teams"] = teams_data
    client.save_games()

    team_color = client.teams[event_name][team_name].get("color", "#FFFFFF")
    team_color_discord = discord.Color(int(team_color.lstrip('#'), 16))

    embed = discord.Embed(
        title=f"Drops Removed for {osrs_ign} from {team_name}",
        color=team_color_discord
    )
    embed.add_field(name=f"Removed Drops ({drops_removed})", value="\n".join(removed_drops_list) if removed_drops_list else "No drops removed.", inline=False)
    embed.add_field(name="Total Points Removed", value=removed_points, inline=False)
    embed.add_field(name="Updated Team Total Points", value=new_team_total_points, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_extravaganza_leaderboard", description="Admin: Shows the team leaderboard and graph.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_extravaganza_leaderboard(interaction: discord.Interaction, event_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_extravaganza_leaderboard with event: {event_name}")

    await interaction.response.defer(ephemeral=True)

    try:
        game_uuid = client.events.get(event_name, {}).get("game_id")
        if not game_uuid:
            await interaction.followup.send(f"Event '{event_name}' not found or game ID missing.", ephemeral=True)
            return

        logging.info(f"Forcing immediate execution of extravaganza_tasks for {game_uuid}")
        await client.execute_extravaganza_task(game_uuid) 
        await interaction.followup.send("Leaderboard and graph sent!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_extravaganza_reset_data", description="Admin: Reset team drop counts and total points for an extravaganza event.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete)
@app_commands.default_permissions(administrator=True)
async def admin_extravaganza_reset_data(interaction: discord.Interaction, event_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_extravaganza_reset_data with event_name: {event_name}")

    confirm_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="✅ Yes, Reset Data")
    cancel_button = discord.ui.Button(style=discord.ButtonStyle.secondary, label="❌ Cancel")

    async def confirm_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            game_uuid = client.events.get(event_name, {}).get("game_id")
            if not game_uuid:
                await interaction_button.response.send_message(f"Event '{event_name}' not found or game ID missing.", ephemeral=True)
                return

            game_data = client.games.get(game_uuid, {}).get("game_data", {})
            if "teams" in game_data:
                game_data["teams"] = {}
            client.save_games()
            await interaction_button.response.send_message(f"Data reset for event '{event_name}'.", ephemeral=True)
            await interaction.edit_original_response(view=None)  # remove buttons
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    async def cancel_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            await interaction_button.response.send_message("Data reset cancelled.", ephemeral=True)
            await interaction.edit_original_response(view=None)  # remove buttons
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(f"Are you sure you want to reset all team data for event {event_name}?", view=view, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_schedule_event_tasks", description="Admin: Schedules tasks for an event.")
@app_commands.autocomplete(event_name=event_name_autocomplete)
@app_commands.default_permissions(administrator=True)
async def schedule_event_tasks(interaction: discord.Interaction, event_name: str):
    logging.info(f"Admin {interaction.user.name} used /schedule_event_tasks with event: {event_name}")

    await interaction.response.defer(ephemeral=True)

    scheduled_tasks = client.load_scheduled_tasks()
    game_uuid = client.events.get(event_name, {}).get("game_id")
    event_type = client.events.get(event_name, {}).get("type")

    if not game_uuid:
        await interaction.followup.send(f"Event '{event_name}' not found or game ID missing.", ephemeral=True)
        return

    if event_type == "extravaganza":
        if game_uuid in scheduled_tasks.get("extravaganza_tasks", []):
            await interaction.followup.send(f"Extravaganza tasks for event '{event_name}' are already scheduled.", ephemeral=True)
        else:
            scheduled_tasks.setdefault("extravaganza_tasks", []).append(game_uuid)
            client.save_scheduled_tasks(scheduled_tasks)
            await interaction.followup.send(f"Extravaganza tasks scheduled for event '{event_name}'.", ephemeral=True)

    elif event_type == "bingo":
        await interaction.followup.send(f"Scheduled tasks for Bingo events are not yet implemented.", ephemeral=True)

    elif event_type == "snakes_ladders":
        await interaction.followup.send(f"Scheduled tasks for Snakes and Ladders events are not yet implemented.", ephemeral=True)

    else:
        await interaction.followup.send(f"Event type '{event_type}' not supported for scheduling.", ephemeral=True)
        return
    
#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="admin_remove_scheduled_task", description="Admin: Removes a scheduled task for an event.")
@app_commands.autocomplete(event_name=scheduled_task_autocomplete)
@app_commands.default_permissions(administrator=True)
async def remove_scheduled_task(interaction: discord.Interaction, event_name: str):
    logging.info(f"Admin {interaction.user.name} used /admin_remove_scheduled_task with event: {event_name}")

    await interaction.response.defer(ephemeral=True)

    scheduled_tasks = client.load_scheduled_tasks()
    game_uuid = client.events.get(event_name, {}).get("game_id")
    event_type = client.events.get(event_name, {}).get("type")

    if not game_uuid:
        await interaction.followup.send(f"Event '{event_name}' not found or game ID missing.", ephemeral=True)
        return

    if event_type == "extravaganza":
        if game_uuid in scheduled_tasks.get("extravaganza_tasks", []):
            scheduled_tasks.get("extravaganza_tasks", []).remove(game_uuid)
            client.save_scheduled_tasks(scheduled_tasks)
            await interaction.followup.send(f"Extravaganza tasks for event '{event_name}' removed.", ephemeral=True)
        else:
            await interaction.followup.send(f"Extravaganza tasks for event '{event_name}' were not scheduled.", ephemeral=True)

    elif event_type == "bingo":
        await interaction.followup.send(f"Scheduled tasks for Bingo events are not yet implemented.", ephemeral=True)

    elif event_type == "snakes_ladders":
        await interaction.followup.send(f"Scheduled tasks for Snakes and Ladders events are not yet implemented.", ephemeral=True)

    else:
        await interaction.followup.send(f"Event type '{event_type}' not supported for removing scheduled tasks.", ephemeral=True)
        return
    

#--------------------------------------------------------------------------------------------------------------------------------------------
# All users commands
#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="join", description="Join and add your Old School RuneScape in-game names.")
@app_commands.describe(
  osrs_igns="Your Old School RuneScape in-game names (comma-separated).",
)
async def join(interaction: discord.Interaction, osrs_igns: str):
  logging.info(f"User {interaction.user.name} used /join to add OSRS names: {osrs_igns}.")
  igns = [ign.strip() for ign in osrs_igns.split(',')]
  
  user_data = {"discord_user": interaction.user.name, "osrs_igns": igns}
  
  client.members[interaction.user.name] = user_data
  client.save_members()

  await interaction.response.send_message(f"Your Old School RuneScape in-game names have been saved: {', '.join(igns)}.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="join_event", description="Join an event as a free agent.")
@app_commands.describe(
  event_name="The name of the event.",
  selected_character="The character to use for this event.",
)
@app_commands.autocomplete(event_name=event_name_user_not_in_autocomplete, selected_character=selected_character_autocomplete)
async def join_event(interaction: discord.Interaction, event_name: str, selected_character: str):
  logging.info(f"User {interaction.user.name} used /join_event to join {event_name} with character {selected_character}.")
  if event_name not in client.events:
    await interaction.response.send_message("Event does not exist.", ephemeral=True)
    return

  if interaction.user.name not in client.members:
    await interaction.response.send_message("You have not registered your OSRS names. Use /join first.", ephemeral=True)
    return

  if selected_character not in client.members[interaction.user.name]["osrs_igns"]:
    await interaction.response.send_message("Invalid character selected.", ephemeral=True)
    return

  user_data = {"discord_user": interaction.user.name, "osrs_ign": selected_character}

  if event_name not in client.free_agents:
    client.free_agents[event_name] = []

  if user_data not in client.free_agents[event_name]:
    client.free_agents[event_name].append(user_data)
    client.save_free_agents()
    await interaction.response.send_message(f"You have joined {event_name} as a free agent with character '{selected_character}'.", ephemeral=True)
  else:
    await interaction.response.send_message(f"You are already a free agent for {event_name}.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="unjoin_event", description="Remove yourself from an event's free agent pool.")
@app_commands.describe(event_name="The name of the event.")
@app_commands.autocomplete(event_name=event_name_user_in_autocomplete)
async def unjoin_event(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /unjoin_event to remove themselves from {event_name}.")

    member_name = interaction.user.name

    if event_name not in client.events:
        await interaction.response.send_message("Event does not exist.", ephemeral=True)
        return

    if member_name not in client.members:
        await interaction.response.send_message(
            "You have not registered your OSRS names. Use /admin_join first.",
            ephemeral=True,
        )
        return

    if event_name in client.free_agents:
        free_agents = client.free_agents[event_name]
        users_to_remove = [agent for agent in free_agents if agent["discord_user"] == member_name]

        if users_to_remove:
            for user_data in users_to_remove:
                free_agents.remove(user_data)
            client.save_free_agents()
            await interaction.response.send_message(
                f"You have been removed from {event_name}'s free agents.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"You are not a free agent for {event_name}.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            f"You are not a free agent for {event_name}.",
            ephemeral=True,
        )

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="event_free_agents_view", description="View free agents for a specific event (team leaders and admins).")
@app_commands.describe(event_name="The name of the event to view free agents for.")
@app_commands.autocomplete(event_name=event_names_in_events_free_agents_autocomplete)
async def event_free_agents_view(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /event_free_agents_view to view free agents for {event_name}.")

    is_admin = interaction.user.guild_permissions.administrator
    is_leader = False

    if not is_admin and event_name in client.teams:
        for team in client.teams[event_name].values():
            for member in team["members"]:
                if member["discord_user"] == interaction.user.name and member["role"] == "leader":
                    is_leader = True
                    break
            if is_leader:
                break

    if not is_admin and not is_leader:
        await interaction.response.send_message(
            "You are not authorized to use this command.", ephemeral=True
        )
        return

    if event_name not in client.free_agents:
        await interaction.response.send_message(f"Event '{event_name}' not found.", ephemeral=True)
        return

    free_agents = client.free_agents[event_name]

    if not free_agents:
        await interaction.response.send_message(f"No free agents found for '{event_name}'.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Free Agents for {event_name}", color=discord.Color.green())

    for agent in free_agents:
        embed.add_field(name=agent['osrs_ign'], value="", inline=False)

    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="event_teams_view", description="View teams and members for a specific event (team leaders and admins).")
@app_commands.describe(event_name="The name of the event to view teams for.")
@app_commands.autocomplete(event_name=event_names_with_teams_autocomplete)
async def event_teams_view(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /event_teams_view to view teams for {event_name}.")

    # Check if the user is an admin or a team leader
    is_admin = interaction.user.guild_permissions.administrator
    is_leader = False

    if not is_admin and event_name in client.teams:
        event_teams = client.teams[event_name]
        for team in event_teams.values():
            for member in team["members"]:
                if member["role"] == "leader" and member["discord_user"] == interaction.user.name:
                    is_leader = True
                    break
            if is_leader:
                break

    if not is_admin and not is_leader:
        await interaction.response.send_message(
            "You are not authorized to use this command.", ephemeral=True
        )
        return

    if event_name not in client.teams:
        await interaction.response.send_message(f"Event '{event_name}' not found.", ephemeral=True)
        return

    event_teams = client.teams[event_name]

    if not event_teams:
        await interaction.response.send_message(f"No teams found for '{event_name}'.", ephemeral=True)
        return

    embeds = []

    title_embed = discord.Embed(title=f"Teams for {event_name}", color=discord.Color.greyple())
    embeds.append(title_embed)

    for team_name, team_data in event_teams.items():
        leaders = []
        members = []
        for member in team_data["members"]:
            if member["role"] == "leader":
                leaders.append(f"- {member['osrs_ign']}")
            else:
                members.append(f"- {member['osrs_ign']}")

        leader_str = f"**Leader(s)**:\n{''.join(leaders)}" if leaders else ""
        member_str = f"**Member(s)**:\n{''.join(members)}" if members else ""

        team_members = f"{leader_str}\n{member_str}".strip()

        color_hex = team_data["color"].lstrip("#")
        try:
            color_int = int(color_hex, 16)
            team_color = discord.Color(color_int)
        except ValueError:
            team_color = discord.Color.default()

        embed = discord.Embed(title=team_name, description=team_members, color=team_color)
        embeds.append(embed)

    await interaction.response.send_message(embeds=embeds)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="team_edit", description="Edit a team's name and color in an event.")
@app_commands.describe(
    event_name="The name of the event.",
    old_team_name="The current name of the team.",
    new_team_name="The new name for the team.",
    new_team_color="The new color for the team (e.g., #FF0000).",
)
@app_commands.autocomplete(event_name=event_name_autocomplete, old_team_name=teams_in_event_autocomplete)
async def team_edit(interaction: discord.Interaction, event_name: str, old_team_name: str, new_team_name: str, new_team_color: str):
    logging.info(f"{interaction.user.name} used /admin_team_edit to edit team {old_team_name} to {new_team_name} with color {new_team_color} in {event_name}.")

    if event_name not in client.events:
        await interaction.response.send_message("Event does not exist.", ephemeral=True)
        return

    if event_name not in client.teams or old_team_name not in client.teams[event_name]:
        await interaction.response.send_message("Team does not exist for this event.", ephemeral=True)
        return

    if new_team_name in client.teams[event_name] and new_team_name != old_team_name:
        await interaction.response.send_message("A team with the new name already exists in this event.", ephemeral=True)
        return

    # Check if the user is an admin or team leader
    is_admin = interaction.user.guild_permissions.administrator
    is_leader = False

    if "members" in client.teams[event_name][old_team_name]:
        for member in client.teams[event_name][old_team_name]["members"]:
            if member.get("discord_user") == interaction.user.name and member.get("role") == "leader":
                is_leader = True
                break

    if not is_admin and not is_leader:
        await interaction.response.send_message("You do not have permission to edit this team.", ephemeral=True)
        return

    # Update team name and color in teams.json
    team_data = client.teams[event_name].pop(old_team_name)
    old_team_color = team_data.get("color")
    team_data["color"] = new_team_color
    client.teams[event_name][new_team_name] = team_data
    client.save_teams()

    # Update team name in games.json
    game_uuid = client.events[event_name]["game_id"]
    if game_uuid in client.games:
        game_data = client.games[game_uuid]["game_data"]
        if "teams" in game_data and old_team_name in game_data["teams"]:
            game_data["teams"][new_team_name] = game_data["teams"].pop(old_team_name)
            client.save_games()

    def create_color_image_combined(color_hex1, color_hex2):
        try:
            color_int1 = int(color_hex1.lstrip('#'), 16)
            r1 = (color_int1 >> 16) & 0xFF
            g1 = (color_int1 >> 8) & 0xFF
            b1 = color_int1 & 0xFF

            color_int2 = int(color_hex2.lstrip('#'), 16)
            r2 = (color_int2 >> 16) & 0xFF
            g2 = (color_int2 >> 8) & 0xFF
            b2 = color_int2 & 0xFF

            img = Image.new('RGBA', (230, 60), (0, 0, 0, 0)) #Fully transparent image
            draw = ImageDraw.Draw(img)
            draw.rectangle((5, 5, 55, 55), fill=(r1, g1, b1, 255)) #Fill with color, full opacity
            draw.rectangle((55, 5, 175, 55), fill=(0, 0, 0, 0))
            draw.rectangle((175, 5, 225, 55), fill=(r2, g2, b2, 255)) #Fill with color, full opacity

            with io.BytesIO() as image_binary:
                img.save(image_binary, 'PNG')
                image_binary.seek(0)
                return discord.File(fp=image_binary, filename='colors.png')
        except ValueError:
            return None

    combined_color_file = create_color_image_combined(old_team_color, new_team_color)

    try:
        color_int = int(new_team_color.lstrip('#'), 16)
        embed_color = discord.Color(color_int)
    except ValueError:
        embed_color = discord.Color.blurple()

    embed = discord.Embed(
        title=f"Team '{old_team_name}' Renamed",
        description=f"Team '{old_team_name}' has been renamed to '{new_team_name}'.",
        color=embed_color
    )

    embed.add_field(name="Old Color", value=f"`{old_team_color}`", inline=True)
    embed.add_field(name="New Color", value=f"`{new_team_color}`", inline=True)

    if combined_color_file:
        embed.set_image(url="attachment://colors.png")

    embed.set_footer(text=f"Event: {event_name}")

    files = []
    if combined_color_file:
        files.append(combined_color_file)

    await interaction.response.send_message(embed=embed, files=files, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="team_assign", description="Add a member to a team (team leaders and admins).")
@app_commands.describe(event_name="The name of the event.", team_name="The name of the team.",
                       free_agent_osrs_ign="The OSRS in-game name of the free agent.", team_role="The role of the free agent (leader or member).")
@app_commands.autocomplete(event_name=event_name_autocomplete, team_name=teams_in_event_autocomplete, free_agent_osrs_ign=free_agent_autocomplete)
@app_commands.choices(
  team_role=[
    app_commands.Choice(name="leader", value="leader"),
    app_commands.Choice(name="member", value="member"),
  ]
)
async def team_assign(interaction: discord.Interaction, event_name: str, team_name: str,
                      free_agent_osrs_ign: str, team_role: str):
  # Check if the user is an admin or a team leader
  is_admin = interaction.user.guild_permissions.administrator
  is_leader = False

  if not is_admin and event_name in client.teams and team_name in client.teams[event_name]:
      for member in client.teams[event_name][team_name]["members"]:
          if member["discord_user"] == interaction.user.name and member["role"] == "leader":
              is_leader = True
              break

  if not is_admin and not is_leader:
      await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
      return
  
  logging.info(f"User {interaction.user.name} used /team_assign to assign {free_agent_osrs_ign} to {team_name} as a {team_role}.")

  if event_name not in client.teams or team_name not in client.teams[event_name]:
    await interaction.response.send_message("Invalid event or team name.", ephemeral=True)
    return

  if event_name not in client.free_agents:
    await interaction.response.send_message("No free agents for this event.", ephemeral=True)
    return

  free_agent_to_assign = None
  for agent in client.free_agents[event_name]:
    if agent["osrs_ign"] == free_agent_osrs_ign:
      free_agent_to_assign = agent
      break

  if not free_agent_to_assign:
    await interaction.response.send_message("Free agent not found.", ephemeral=True)
    return

  team_color = client.teams[event_name][team_name]["color"]

  client.teams[event_name][team_name]["members"].append(
    {"role": team_role, **free_agent_to_assign}
  )

  client.free_agents[event_name].remove(free_agent_to_assign)
  client.save_teams()
  client.save_free_agents()

  embed = discord.Embed(
    title="Free Agent Assigned!",
    description=f"{free_agent_osrs_ign} assigned to {team_name} as a {team_role}.",
    color=int(team_color[1:], 16),
  )
  await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="team_unassign", description="Un-add a member to a team and moved them back to the free agent pool (team leaders and admins).")
@app_commands.describe(member_ign="The OSRS IGN to unassign.", event_name="The event to unassign from.")
@app_commands.autocomplete(member_ign=team_member_ign_autocomplete, event_name=team_event_autocomplete_for_member_ign)
async def team_unassign(interaction: discord.Interaction, member_ign: str, event_name: str):
    # Check if the user is an admin or a team leader
    is_admin = interaction.user.guild_permissions.administrator
    is_leader = False

    if not is_admin and event_name in client.teams:
        for team in client.teams[event_name].values():
            for member in team["members"]:
                if member["discord_user"] == interaction.user.name and member["role"] == "leader":
                    is_leader = True
                    break
            if is_leader:
                break

    if not is_admin and not is_leader:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    logging.info(f"User {interaction.user.name} used /team_unassign to unassign {member_ign} from {event_name}.")

    if event_name not in client.teams:
        await interaction.response.send_message("Invalid event name.", ephemeral=True)
        return

    team_found = False
    for team_name, team in client.teams[event_name].items():
        member_index = None
        for index, member in enumerate(team["members"]):
            if member["osrs_ign"] == member_ign:
                member_index = index
                member_to_unassign = member
                break
        if member_index is not None:
            team["members"].pop(member_index)
            team_found = True
            break

    if not team_found:
        await interaction.response.send_message("Member not found in any team for this event.", ephemeral=True)
        return

    if event_name not in client.free_agents:
        client.free_agents[event_name] = []

    client.free_agents[event_name].append({
        "discord_user": member_to_unassign["discord_user"],
        "osrs_ign": member_to_unassign["osrs_ign"],
    })

    client.save_teams()
    client.save_free_agents()

    await interaction.response.send_message(f"{member_ign} unassigned from a team in {event_name} and moved to free agents.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="draw_board", description="Draws the bingo or snakes and ladders board.")
@app_commands.describe(event_name="The name of the bingo or snakes and ladders event.")
@app_commands.autocomplete(event_name=bingo_snakes_event_autocomplete)
async def draw_board(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /draw_board to draw {event_name}.")
    if event_name not in client.events:
        await interaction.response.send_message("Event not found.", ephemeral=True)
        return

    event_data = client.events[event_name]
    game_uuid = event_data["game_id"]

    if game_uuid not in client.games:
        await interaction.response.send_message("Game data not found.", ephemeral=True)
        return

    game_data = client.games[game_uuid]["game_data"]

    if event_data["type"] == "bingo":
        board = game_data["board"]
        board_image = await draw_bingo_board_image(board)
        bingo_image = await draw_bingo_text_image(50, len(board), 3, 10)  # Cell size halved

        board_pil = Image.open(board_image.fp)
        bingo_pil = Image.open(bingo_image.fp)

        combined_image = Image.new("RGBA", (board_pil.width, board_pil.height + bingo_pil.height), (43, 43, 43, 255))
        combined_image.paste(bingo_pil, (0, 0))
        combined_image.paste(board_pil, (0, bingo_pil.height))

        buffer = io.BytesIO()
        combined_image.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(buffer, filename="combined_bingo.png")

        await interaction.response.send_message(file=file)

    elif event_data["type"] == "snakes_ladders":
        board = game_data["board"]
        snakes = game_data["snakes"]
        ladders = game_data["ladders"]

        # Get the teams for the event
        teams = client.teams.get(event_name, {})

        # Create pawns data based on teams and team colors
        pawns = []

        for team_name, team_data in teams.items():

            team_color = team_data.get("color", (245, 245, 220))  # Get color from team data, default to light beige
            pawn_history = game_data.get("pawns", {}).get(team_name, [0]) #get the pawns history or start with [0]

            if isinstance(pawn_history, int):
                pawn_history = [pawn_history]

            pawn_position = pawn_history[-1] #get the latest position

            pawns.append({
                "name": team_name,
                "position": pawn_position,
                "color": team_color,
                "outline": "black"
            })

        image = await draw_snakes_ladders_board_image(board, snakes, ladders, pawns)

        if image:
            await interaction.response.send_message(file=image)
        else:
            await interaction.response.send_message("Failed to generate the Snakes and Ladders board image. Please check the image folders.", ephemeral=True)
    else:
        await interaction.response.send_message("This command only works for bingo and snakes and ladders events.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="list_snakes_ladders_tasks", description="Lists all tasks in a Snakes and Ladders event.")
@app_commands.describe(event_name="The name of the Snakes and Ladders event.", public="Make the announcement public? (Admin only)")
@app_commands.autocomplete(event_name=snakes_ladders_event_autocomplete)
async def list_snakes_ladders_tasks(interaction: discord.Interaction, event_name: str, public: bool = False):
    logging.info(f"User {interaction.user.name} used /list_snakes_ladders_tasks for {event_name}. Public: {public}")
    if event_name not in client.events:
        await interaction.response.send_message("Event not found.", ephemeral=True)
        return

    event_data = client.events[event_name]
    if event_data["type"] != "snakes_ladders":
        await interaction.response.send_message("This command only works for Snakes and Ladders events.", ephemeral=True)
        return

    game_uuid = event_data["game_id"]
    if game_uuid not in client.games:
        await interaction.response.send_message("Game data not found.", ephemeral=True)
        return

    game_data = client.games[game_uuid]["game_data"]
    board = game_data["board"]

    snakes = game_data.get("snakes", [])
    ladders = game_data.get("ladders", [])

    embeds = []  # List to store multiple embeds

    snake_starts = {start + 1: end + 1 for start, end in snakes}
    snake_ends = {end + 1: start + 1 for start, end in snakes}
    ladder_starts = {start + 1: end + 1 for start, end in ladders}
    ladder_ends = {end + 1: start + 1 for start, end in ladders}

    page_size = 25
    for page in range(4):
        start_index = page * page_size
        end_index = start_index + page_size
        page_board = board[start_index:end_index]
        page_num = page + 1
        embed = discord.Embed(title=f"Snakes and Ladders Tasks - {event_name} (Page {page_num}/5)", color=discord.Color.blurple())
        task_list = ""
        for index, task in enumerate(page_board):
            task_num = start_index + index + 1
            indicator = ""
            if task_num in snake_starts:
                indicator = f" *:snake: to {snake_starts[task_num]}*"
            elif task_num in snake_ends:
                indicator = f" *:snake: from {snake_ends[task_num]}*"
            elif task_num in ladder_starts:
                indicator = f" *:ladder: to {ladder_starts[task_num]}*"
            elif task_num in ladder_ends:
                indicator = f" *:ladder: from {ladder_ends[task_num]}*"

            if task is None:
                if indicator:
                    task_list += f"{task_num}. {indicator}\n"
                else:
                    task_list += f"{task_num}. *NULL*\n"
            elif isinstance(task, str):
                task_list += f"{task_num}. {task}{indicator}\n"
            elif isinstance(task, list):
                names = [item["name"] for item in task]
                task_list += f"{task_num}. {', '.join(names)}{indicator}\n"
        embed.description = task_list
        embeds.append(embed)

    # Create the fifth embed for snakes and ladders
    embed_snakes_ladders = discord.Embed(title=f"Snakes and Ladders - {event_name}", color=discord.Color.green())
    snake_list = "\n".join([f"{start + 1} to {end + 1}" for start, end in snakes]) if snakes else "None"
    ladder_list = "\n".join([f"{start + 1} to {end + 1}" for start, end in ladders]) if ladders else "None"
    embed_snakes_ladders.add_field(name=":snake: Snakes", value=snake_list, inline=False)
    embed_snakes_ladders.add_field(name=":ladder: Ladders", value=ladder_list, inline=False)
    embeds.append(embed_snakes_ladders)

    if public and interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(embeds=embeds)
    else:
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="roll_dice", description="Team Leader: Rolls a dice for Snakes and Ladders.")
@app_commands.describe(event_name="The name of the Snakes and Ladders event.")
@app_commands.autocomplete(event_name=snakes_ladders_event_autocomplete)
async def roll_dice(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /roll_dice for {event_name}.")
    if event_name not in client.events:
        await interaction.response.send_message("Event not found.", ephemeral=True)
        return

    event_data = client.events[event_name]
    if event_data["type"] != "snakes_ladders":
        await interaction.response.send_message("This command only works for Snakes and Ladders events.", ephemeral=True)
        return

    game_uuid = event_data["game_id"]
    if game_uuid not in client.games:
        await interaction.response.send_message("Game data not found.", ephemeral=True)
        return

    game_data = client.games[game_uuid]["game_data"]
    teams = client.teams.get(event_name, {})

    if not teams:
        await interaction.response.send_message("No teams found for this event.", ephemeral=True)
        return

    # Check if the user is on a team and is a leader
    user_team = None
    for team_name, team_data in teams.items():
        for member in team_data["members"]:
            # if member["discord_user"] == interaction.user.name and member["role"] == "leader":
            #     user_team = team_name
            #     break
            user_team = team_name
            break
        if user_team:
            break

    if not user_team:
        await interaction.response.send_message("You are not a team leader for this event.", ephemeral=True)
        return

    current_team_name = user_team #Use the user team name

    # Roll the dice
    dice_roll = random.randint(1, 6)

    # Update pawn position
    pawn_history = game_data.get("pawns", {}).get(current_team_name, [0]) #get the pawns history or start with [0]
    current_position = pawn_history[-1] #get the latest position
    new_position = current_position + dice_roll

    # Check for snakes and ladders
    snakes = game_data.get("snakes", [])
    ladders = game_data.get("ladders", [])

    snake_or_ladder_message = ""

    for start, end in snakes:
        if new_position == start:
            new_position = end
            snake_or_ladder_message = "Oh no, oh no! You landed on a snake :snake: and slid down."
            break

    for start, end in ladders:
        if new_position == start:
            new_position = end
            snake_or_ladder_message = "Yay! You landed on a ladder :ladder: and climbed up."
            break

    # Update pawn position in game data
    if "pawns" not in game_data:
        game_data["pawns"] = {}

    if current_team_name not in game_data["pawns"]:
        game_data["pawns"][current_team_name] = [0] #initializes the array if it does not exist

    game_data["pawns"][current_team_name].append(new_position) #append the new position to the array.

    client.save_games()

    # Get the team color
    team_data = teams[current_team_name]
    team_color_hex = team_data.get("color", "#FFFFFF")  # Default to white if no color
    team_color = discord.Color.from_str(team_color_hex)

    description = f"Rolled a {dice_roll} and moved from {current_position + 1} to {new_position + 1}."
    if snake_or_ladder_message:
        description += f"\n{snake_or_ladder_message}"

    # Create the embed
    embed = discord.Embed(
        title=f":game_die: {current_team_name} Dice Roll",
        description=description,
        color=team_color,
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)

    await draw_and_send_board(interaction, game_data, teams)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="revert_roll", description="Team Leader: Reverts the last dice roll for Snakes and Ladders.")
@app_commands.describe(event_name="The name of the Snakes and Ladders event.", reason="Reason for reverting the roll.")
@app_commands.autocomplete(event_name=snakes_ladders_event_autocomplete)
async def revert_roll(interaction: discord.Interaction, event_name: str, reason: str="No reason provided"):
    logging.info(f"User {interaction.user.name} used /revert_roll for {event_name}.")
    if event_name not in client.events:
        await interaction.response.send_message("Event not found.", ephemeral=True)
        return

    event_data = client.events[event_name]
    if event_data["type"] != "snakes_ladders":
        await interaction.response.send_message("This command only works for Snakes and Ladders events.", ephemeral=True)
        return

    game_uuid = event_data["game_id"]
    if game_uuid not in client.games:
        await interaction.response.send_message("Game data not found.", ephemeral=True)
        return

    game_data = client.games[game_uuid]["game_data"]
    teams = client.teams.get(event_name, {})

    if not teams:
        await interaction.response.send_message("No teams found for this event.", ephemeral=True)
        return

    # Check if the user is on a team and is a leader
    user_team = None
    for team_name, team_data in teams.items():
        for member in team_data["members"]:
            if member["discord_user"] == interaction.user.name and member["role"] == "leader":
                user_team = team_name
                break
        if user_team:
            break

    if not user_team:
        await interaction.response.send_message("You are not a team leader for this event.", ephemeral=True)
        return

    current_team_name = user_team

    pawn_history = game_data.get("pawns", {}).get(current_team_name, [0])

    if len(pawn_history) <= 1:
        await interaction.response.send_message("No rolls to revert.", ephemeral=True)
        return

    confirm_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="✅ Yes, Revert Roll. I understand there is no going back!")
    cancel_button = discord.ui.Button(style=discord.ButtonStyle.secondary, label="❌ Cancel")

    async def confirm_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            previous_position = pawn_history[-2] if len(pawn_history) > 1 else 0 #get the position before the last one.
            current_position = pawn_history[-1] #get the latest position.

            pawn_history.pop()  # Remove the last position
            client.save_games()

            # Get the team color
            team_data = teams[current_team_name]
            team_color_hex = team_data.get("color", "#FFFFFF")  # Default to white if no color
            team_color = discord.Color.from_str(team_color_hex)

            # Create the embed
            embed = discord.Embed(
                title=f":leftwards_arrow_with_hook: {current_team_name} Roll Reverted",
                description=f"Last roll reverted from {current_position + 1} to {previous_position + 1}.",
                color=team_color,
            )

            await interaction_button.response.send_message(embed=embed, ephemeral=False)
            await interaction.edit_original_response(view=None)  # Remove buttons
            await draw_and_send_board(interaction, game_data, teams)
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    async def cancel_callback(interaction_button: discord.Interaction):
        if interaction_button.user == interaction.user:
            await interaction_button.response.send_message("Roll reversion cancelled.", ephemeral=True)
            await interaction.edit_original_response(view=None)  # Remove buttons
        else:
            await interaction_button.response.send_message("This is not your button to press", ephemeral=True)

    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(f"Are you sure you want to revert the last roll for {current_team_name}? THERE IS NO GOING BACK.", view=view, ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_boss_drops", description="View drops and points for a boss.")
@app_commands.autocomplete(boss_name=boss_autocomplete)
async def extravaganza_boss_drops(interaction: discord.Interaction, boss_name: str):
    logging.info(f"User {interaction.user.name} used /extravaganza_boss_drops: boss={boss_name}")
    
    boss_drops = client.drops
    if boss_name not in boss_drops:
        await interaction.response.send_message(f"Boss '{boss_name}' not found.", ephemeral=True)
        return

    boss_data = boss_drops[boss_name]
    embed = discord.Embed(title=f"{boss_name}", color=discord.Color.blurple())
    drops = boss_data.get("drops", {})
    image_path = boss_data.get("image")

    file = None
    if image_path and os.path.exists(image_path):
        file = discord.File(image_path, filename=os.path.basename(image_path))
        embed.set_thumbnail(url=f"attachment://{os.path.basename(image_path)}")

    # Add drops to the embed, but break it into multiple embeds if there are too many
    embeds = []
    current_embed = embed
    for drop_name, points in drops.items():
        current_embed.add_field(name=drop_name, value=f"Points: {points}", inline=False)
        if len(current_embed.fields) >= 25:  # If there are too many fields in one embed
            embeds.append(current_embed)
            current_embed = discord.Embed(title=f"{boss_name}", color=discord.Color.blue())
            if image_path and os.path.exists(image_path):
                current_embed.set_thumbnail(url=f"attachment://{os.path.basename(image_path)}")
            current_embed.add_field(name="Warning", value=f"Too many drops for {boss_name}. Some drops may not be shown.", inline=False)
    # Add the last embed
    embeds.append(current_embed)

    if not embeds:
        return await interaction.response.send_message("No drops found for this boss.", ephemeral=True)

    # Send embeds (if there's only one embed, it sends as a single message)
    if len(embeds) == 1:
        await interaction.response.send_message(embed=embeds[0], files=[file] if file else [], ephemeral=True)
    else:
        for embed in embeds:
            await interaction.followup.send(embed=embed, files=[file] if file else [])

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_drop", description="Enter boss drop for your team.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_member_name=team_member_autocomplete, boss_name=boss_autocomplete, drop_name=drop_autocomplete)
async def extravaganza_drop(interaction: discord.Interaction, event_name: str, team_member_name: str, boss_name: str, drop_name: str):
    logging.info(f"User {interaction.user.name} used /extravaganza_drop to enter drop {drop_name} for {boss_name} in {event_name}.")

    member_id = str(interaction.user.name)

    team_found = None
    teams = client.teams
    if event_name in teams:
        for team, team_details in teams[event_name].items():
            for member in team_details["members"]:
                if member["discord_user"] == member_id:
                    team_found = team
                    team_color = team_details.get("color", "#FFFFFF")
                    break
            if team_found:
                break

    if not team_found:
        return await interaction.response.send_message(f"❌ User '{member_id}' not found in any team roster for event '{event_name}'.")

    # Get the osrs_ign from the selected team_member_name (Discord user ID).
    for member in client.teams[event_name][team_found]["members"]:
        if member["discord_user"] == team_member_name:
            osrs_ign = member["osrs_ign"]
            break
    else:
        return await interaction.response.send_message(f"❌ Member '{team_member_name}' not found in team '{team_found}'.", ephemeral=True)

    message, original_points, added_points, new_total_points = process_drop_data(event_name, team_found, team_member_name, osrs_ign, boss_name, drop_name)

    if message.startswith("❌"):
        return await interaction.response.send_message(message)

    team_color_discord = discord.Color(int(team_color.lstrip('#'), 16))
    embed = discord.Embed(
        description=f"{message}\n"
                    f"**Original points**: {int(original_points)}\n"
                    f"**Added points**: {int(added_points)}\n"
                    f"**New total points**: {int(new_total_points)}",
        color=team_color_discord
    )
    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_drop_remove", description="Remove a drop from a team member.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_member_name=drop_remove_member_autocomplete, boss_name=team_boss_autocomplete, drop_name=team_drop_autocomplete)
async def extravaganza_drop_remove(interaction: discord.Interaction, event_name: str, team_member_name: str, boss_name: str, drop_name: str):
    logging.info(f"User {interaction.user.name} used /extravaganza_drop_remove to remove drop {drop_name} for {boss_name} in {event_name}.")

    member_id = str(interaction.user.name)
    team_name = None
    teams = client.teams
    if event_name in teams:
        for team, team_details in teams[event_name].items():
            for member in team_details["members"]:
                if member["discord_user"] == member_id and member["role"] == "leader":
                    team_name = team
                    break
            if team_name:
                break

    if not team_name:
        return await interaction.response.send_message("You are not a team leader for this event.", ephemeral=True)

    # Get the osrs_ign from the selected discord user.
    for member in client.teams[event_name][team_name]["members"]:
        if member["discord_user"] == team_member_name:
            osrs_ign = member["osrs_ign"]
            break
    else:
        return await interaction.response.send_message(f"❌ Member '{team_member_name}' not found in team '{team_name}'.", ephemeral=True)

    message, original_points, removed_points, new_total_points = process_drop_removal(event_name, team_name, team_member_name, osrs_ign, boss_name, drop_name)

    if message.startswith("❌"):
        return await interaction.response.send_message(message, ephemeral=True)

    team_color = client.teams[event_name][team_name]["color"]
    team_color_discord = discord.Color(int(team_color.lstrip('#'), 16))
    embed = discord.Embed(
        title=f"🗑️ {team_name} - {event_name}",
        description=f"{message}\n"
                    f"**Original points**: {int(original_points)}\n"
                    f"**Points removed**: {int(removed_points)}\n"
                    f"**New total points**: {int(new_total_points)}",
        color=team_color_discord
    )
    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_player_points_all", description="Get total points for each player in an event, separated by teams with team colors in one message.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete)
async def extravaganza_player_points_all(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /extravaganza_player_points_all for event {event_name}.")

    events_data = client.events
    games_data = client.games
    teams_data = client.teams

    if event_name not in events_data:
        return await interaction.response.send_message(f"❌ Event '{event_name}' not found.", ephemeral=True)

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return await interaction.response.send_message(f"❌ Game data for '{event_name}' not found.", ephemeral=True)

    game_data = games_data[game_id]["game_data"]
    teams_data = game_data.get("teams", {})

    if not teams_data:
        return await interaction.response.send_message(f"No team points data found for '{event_name}'.", ephemeral=True)

    embeds = []

    # Create title embed
    title_embed = discord.Embed(
        title=f"{event_name} - Total Player Points",
        color=discord.Color.blurple()
    )
    embeds.append(title_embed)

    for team_name, team_data in teams_data.items():
        player_points = {}
        if "drops" in team_data:
            for boss_drops in team_data["drops"].values():
                for drop_entries in boss_drops.values():
                    for point_entry in drop_entries["points"]:
                        for player_name, points in point_entry.items():
                            if player_name not in player_points:
                                player_points[player_name] = 0
                            player_points[player_name] += points

        if not player_points:
            continue  # Skip teams with no player points

        message = ""
        for player_name, total_points in sorted(player_points.items(), key=lambda item: item[1], reverse=True):
            # Find osrs_ign from teams_data
            osrs_ign = None
            if event_name in teams_data and team_name in teams_data[event_name]:
                for member in teams_data[event_name][team_name]["members"]:
                    if member["discord_user"] == player_name:
                        osrs_ign = member["osrs_ign"]
                        break
            message += f"- {osrs_ign if osrs_ign else player_name}: {total_points}\n"

        team_color = None
        if event_name in teams_data and team_name in teams_data[event_name]:
            team_color_hex = teams_data[event_name][team_name]["color"]
            team_color = discord.Color(int(team_color_hex.lstrip('#'), 16))

        embed = discord.Embed(
            title=f"{team_name}",
            description=message,
            color=team_color if team_color else discord.Color.blue()
        )
        embeds.append(embed)

    if embeds:
        await interaction.response.send_message(embeds=embeds)
    else:
        await interaction.response.send_message(f"No player points data found for '{event_name}'.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_team_stats_all", description="View drop counts and total points for all teams.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete)
async def extravaganza_team_stats_all(interaction: discord.Interaction, event_name: str):
    logging.info(f"User {interaction.user.name} used /extravaganza_team_stats_all for event {event_name}.")

    games_data = client.games
    teams_data = client.teams
    events_data = client.events

    if event_name not in events_data:
        return await interaction.response.send_message(f"Event '{event_name}' not found.", ephemeral=True)

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return await interaction.response.send_message("No game data found.", ephemeral=True)

    game_data = games_data[game_id]["game_data"]
    teams_data = game_data.get("teams", {})

    if not teams_data:
        return await interaction.response.send_message("No team stats available yet.", ephemeral=True)

    embeds = []
    team_total_points = {}

    for team_name, team_data in teams_data.items():
        team_color = None
        if event_name in teams_data and team_name in teams_data[event_name]:
            team_color_hex = teams_data[event_name][team_name]["color"]
            team_color = discord.Color(int(team_color_hex.lstrip('#'), 16))
        else:
            team_color = discord.Color.default()

        embed = discord.Embed(title=f"{team_name} Stats", color=team_color)
        stats_text = ""

        if "drops" in team_data:
            for boss_name, drops in team_data["drops"].items():
                for drop_name, drop_info in drops.items():
                    count = drop_info.get("count", 0)
                    stats_text += f"- {drop_name} from {boss_name}: {count} times\n"

        total_points = team_data.get("total_points", 0)
        team_total_points[team_name] = total_points
        total_points_display = int(total_points) if isinstance(total_points, (int, float)) and total_points.is_integer() else total_points
        stats_text += f"**Total Points: {total_points_display}**\n"
        embed.description = stats_text
        embeds.append(embed)

    if not embeds:
        await interaction.response.send_message("No team stats available yet.")
        return

    total_points_list = list(team_total_points.values())
    leaderboard_embeds = []

    if all(points == 0 for points in total_points_list):
        leader_text = "**No team is currently leading.**"
        leader_embed = discord.Embed(description=leader_text, color=discord.Color.default())
        leaderboard_embeds.append(leader_embed)
    else:
        leader = max(team_total_points, key=team_total_points.get)
        leader_points = team_total_points[leader]
        leader_points_display = int(leader_points) if isinstance(leader_points, (int, float)) and leader_points.is_integer() else leader_points

        leader_color = None
        if event_name in teams_data and leader in teams_data[event_name]:
            leader_color_hex = teams_data[event_name][leader]["color"]
            leader_color = discord.Color(int(leader_color_hex.lstrip('#'), 16))
        else:
            leader_color = discord.Color.default()

        leader_text = f"**Current Leader:** {leader} with {leader_points_display} points."
        leader_embed = discord.Embed(description=leader_text, color=leader_color)
        leaderboard_embeds.append(leader_embed)

        sorted_teams = sorted(team_total_points.items(), key=lambda item: item[1], reverse=True)
        second_place = sorted_teams[1] if len(sorted_teams) > 1 else None
        third_place = sorted_teams[2] if len(sorted_teams) > 2 else None

        if second_place:
            second_place_text = f"**Second Place:** {second_place[0]} with {second_place[1]} points."
            second_place_embed = discord.Embed(description=second_place_text, color=team_color if (event_name in teams_data and second_place[0] in teams_data[event_name] and (team_color_hex := teams_data[event_name][second_place[0]]["color"]) and (team_color := discord.Color(int(team_color_hex.lstrip('#'), 16)))) else discord.Color.default())
            leaderboard_embeds.append(second_place_embed)

        if third_place:
            third_place_text = f"**Third Place:** {third_place[0]} with {third_place[1]} points."
            third_place_embed = discord.Embed(description=third_place_text, color=team_color if (event_name in teams_data and third_place[0] in teams_data[event_name] and (team_color_hex := teams_data[event_name][third_place[0]]["color"]) and (team_color := discord.Color(int(team_color_hex.lstrip('#'), 16)))) else discord.Color.default())
            leaderboard_embeds.append(third_place_embed)

    await interaction.response.send_message(embeds=embeds)
    await interaction.channel.send(embeds=leaderboard_embeds)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="extravaganza_team_stats", description="View drop counts and total points for your team or a specified team.")
@app_commands.autocomplete(event_name=extravaganza_event_autocomplete, team_name=teams_in_event_autocomplete)
async def extravaganza_team_stats(interaction: discord.Interaction, event_name: str, team_name: str = None):
    logging.info(f"User {interaction.user.name} used /extravaganza_team_stats for event {event_name}.")

    games_data = client.games
    teams_data = client.teams
    events_data = client.events
    member_id = str(interaction.user.name)

    if event_name not in events_data:
        return await interaction.response.send_message(f"Event '{event_name}' not found.", ephemeral=True)

    if team_name is None:
        # Determine team_name from user
        team_name = None
        if event_name in teams_data:
            for potential_team_name, team_info in teams_data[event_name].items():
                for member in team_info.get("members", []):
                    if member.get("discord_user") == member_id:
                        team_name = potential_team_name
                        break
                if team_name:
                    break

        if not team_name:
            return await interaction.response.send_message(f"User '{member_id}' is not in any team for event '{event_name}'.", ephemeral=True)

    if event_name not in teams_data or team_name not in teams_data[event_name]:
        return await interaction.response.send_message(f"Team '{team_name}' not found in event '{event_name}'.", ephemeral=True)

    game_id = events_data[event_name]["game_id"]

    if game_id not in games_data:
        return await interaction.response.send_message("No game data found.", ephemeral=True)

    game_data = games_data[game_id]["game_data"]
    teams_data = game_data.get("teams", {})

    if team_name not in teams_data:
        return await interaction.response.send_message(f"No stats found for team '{team_name}'.", ephemeral=True)

    team_color = None
    if event_name in teams_data and team_name in teams_data[event_name]:
        team_color_hex = teams_data[event_name][team_name]["color"]
        team_color = discord.Color(int(team_color_hex.lstrip('#'), 16))
    else:
        team_color = discord.Color.default()

    embed = discord.Embed(title=f"{team_name} Stats", color=team_color)
    stats_text = ""

    team_data = teams_data[team_name]
    if "drops" in team_data:
        for boss_name, drops in team_data["drops"].items():
            for drop_name, drop_info in drops.items():
                count = drop_info.get("count", 0)
                stats_text += f"- {drop_name} from {boss_name}: {count} times\n"

    total_points = team_data.get("total_points", 0)
    total_points_display = int(total_points) if isinstance(total_points, (int, float)) and total_points.is_integer() else total_points
    stats_text += f"**Total Points: {total_points_display}**\n"
    embed.description = stats_text

    await interaction.response.send_message(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------

@client.tree.command(name="help", description="Displays a list of available commands.")
async def help_command(interaction: discord.Interaction):
    logging.info(f"User {interaction.user.name} used /help.")
    commands = client.tree.get_commands()

    general_commands = []
    leader_admin_commands = []
    admin_commands = []

    for command in commands:
        if command.name in ["event_free_agents_view", "event_teams_view", "team_assign", "team_unassign"]:
            leader_admin_commands.append(command)
        elif command.default_permissions and command.default_permissions.administrator:
            if interaction.user.guild_permissions.administrator:
                admin_commands.append(command)
        else:
            general_commands.append(command)

    embeds = []

    if general_commands:
        embed = discord.Embed(title="Available Commands - Page 1", color=discord.Color.blurple())
        general_value = "\n".join([f"**/{cmd.name}**: {cmd.description}" for cmd in general_commands])
        embed.add_field(name="General Commands", value=general_value, inline=False)
        embeds.append(embed)

    if leader_admin_commands:
        embed = discord.Embed(title="Available Commands - Page 2", color=discord.Color.blurple())
        leader_value = "\n".join([f"**/{cmd.name}**: {cmd.description}" for cmd in leader_admin_commands])
        embed.add_field(name="Team Leader/Admin Commands", value=leader_value, inline=False)
        embeds.append(embed)

    if admin_commands and interaction.user.guild_permissions.administrator:
        commands_per_page = 10  # Change this value to adjust the number of commands per page
        admin_command_list = [f"**/{cmd.name}**: {cmd.description}" for cmd in admin_commands]
        admin_pages = [admin_command_list[i:i + commands_per_page] for i in range(0, len(admin_command_list), commands_per_page)]

        page_num = 3  # Start page numbering after general and leader/admin
        for page in admin_pages:
            embed = discord.Embed(title=f"Available Commands - Admin Page {page_num}", color=discord.Color.blurple())
            admin_value = "\n".join(page)
            embed.add_field(name="Admin-Only Commands", value=admin_value, inline=False)
            embeds.append(embed)
            page_num += 1

    if embeds:
        await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        for additional_embed in embeds[1:]:
            await interaction.followup.send(embed=additional_embed, ephemeral=True)
    else:
        await interaction.response.send_message("No commands available.", ephemeral=True)

#--------------------------------------------------------------------------------------------------------------------------------------------

client.run(os.environ.get("DISCORD_TOKEN"))