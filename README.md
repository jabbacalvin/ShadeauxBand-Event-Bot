# Shadeauxband Events Bot Documentation

## Introduction

The Shadeauxband Events Bot is a Discord bot designed to manage and track events, drop logs, and team scores for the Shadeauxband community.

## Getting Started

1.  **Invite the Bot:** [Invite Link Here](https://discord.com/oauth2/authorize?client_id=1349968604636119061&permissions=8&integration_type=0&scope=bot+applications.commands)
2.  **Permissions:** The bot requires "Read Messages," "Send Messages," "Embed Links," and "Administrator" permissions.
3.  **Initial Setup:** Use the `/create_event` command to start a new event.

## Command Reference

### General Commands

- `/join`: Join and add your Old School RuneScape in-game names.
  - Usage: `/join osrs_igns:IGN1, IGN2, IGN3`
  - Note:
    - `osrs_igns` is a comma-separated list of your Old School RuneScape in-game names.
    - This command registers your OSRS in-game names with the bot, associating them with your Discord username.
    - The provided names will be saved for use in events and other bot functionalities.
- `/join_event`: Join an event as a free agent.
  - Usage: `/join_event event_name:MyEvent selected_character:IGN1`
  - Note:
    - `event_name` uses autocomplete to select an event you are not already in.
    - `selected_character` uses autocomplete to select one of your registered OSRS in-game names.
    - You must register your OSRS in-game names using `/join` before joining an event.
    - This command adds you to the free agent pool for the specified event, using the selected OSRS character.
    - If you are already a free agent for the event, a message indicating this will be sent.
    - If the event does not exist or the character is invalid, an error message will be sent.
- `/unjoin_event`: Remove yourself from an event's free agent pool.
  - Usage: `/unjoin_event event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select an event you are currently a free agent in.
    - This command removes you from the free agent pool for the specified event.
    - You must have registered your OSRS names using `/join` before you can unjoin an event.
    - If you are not a free agent for the event, a message indicating this will be sent.
    - If the event does not exist, an error message will be sent.
- `/draw_board`: Draws the bingo or snakes and ladders board.
  - Usage: `/draw_board event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select a bingo or snakes and ladders event.
    - This command draws and displays the game board for the specified event.
    - For bingo events, it combines the bingo board and a text representation of the board into a single image.
    - For snakes and ladders events, it draws the game board with snakes, ladders, and team pawns with their respective positions and colors.
    - If the event or game data is not found, an error message will be sent.
    - If the event type is not bingo or snakes and ladders, an error message will be sent.
    - If the snakes and ladders image generation fails, an error message will be sent.
- `/list_snakes_ladders_tasks`: Lists all tasks in a Snakes and Ladders event.
  - Usage: `/list_snakes_ladders_tasks event_name:MySnakesLaddersEvent public:True/False`
  - Note:
    - `event_name` uses autocomplete to select a Snakes and Ladders event.
    - `public` (optional): If `True`, the list is sent as a public message. If `False` or omitted, the list is sent as an ephemeral message (visible only to the user). Only administrators can set this to `True`.
    - This command provides a detailed list of all tasks on the Snakes and Ladders board, divided into pages of 25 tasks each.
    - For each tile, it displays the task or indicates snake/ladder locations with emojis, and shows _NULL_ for empty, non-snake/ladder tiles.
    - A separate page displays the list of snakes and ladders, showing the start and end tile numbers.
    - If the event is not found or is not a Snakes and Ladders event, an error message will be sent.
    - If the game data is missing, an error message will be sent.
- `/roll_dice`: Team Leader: Rolls a dice for Snakes and Ladders.
  - Usage: `/roll_dice event_name:MySnakesLaddersEvent`
  - Note:
    - `event_name` uses autocomplete to select a snakes and ladders event.
    - This command rolls a dice for the team leader's team in the specified snakes and ladders event.
    - Only team leaders can use this command.
    - If you are not a team leader, an error message will be sent.
    - If the event is not found, is not a snakes and ladders event, or game data is missing, an error message will be sent.
    - If no teams are found for the event, an error message will be sent.
    - The command rolls a 6-sided dice, updates the team's pawn position, and sends an embed with the dice roll result.
    - It also checks for snakes and ladders and updates the pawn position accordingly, sending a message within the embed if a snake or ladder was encountered.
    - The embed message is the color of the team.
    - It then redraws and sends the updated snakes and ladders board with the new pawn positions.
    - If the snakes and ladders image generation fails, an error message will be sent.
- `/revert_roll`: Team Leader: Reverts the last dice roll for Snakes and Ladders.
  - Usage: `/revert_roll event_name:MySnakesLaddersEvent`
  - Note:
    - `event_name` uses autocomplete to select a snakes and ladders event.
    - This command reverts the last dice roll for the team leader's team in the specified snakes and ladders event.
    - Only team leaders can use this command.
    - If you are not a team leader, an error message will be sent.
    - If the event is not found, is not a snakes and ladders event, or game data is missing, an error message will be sent.
    - If no teams are found for the event, an error message will be sent.
    - If there are no rolls to revert, an error message will be sent.
    - The command presents a confirmation dialog with "Yes, Revert Roll" and "Cancel" options.
    - If confirmed, it removes the last pawn position, saves the game data, and sends an embed message indicating the roll was reverted from X to Y, using the team's color.
    - It then redraws and sends the updated snakes and ladders board with the reverted pawn positions.
    - If cancelled, it sends a message indicating the roll reversion was cancelled.
    - If the snakes and ladders image generation fails, an error message will be sent.
- `/extravaganza_boss_drops`: View drops and points for a boss.
  - Usage: `/extravaganza_boss_drops boss_name:BossName`
  - Note:
    - `boss_name` uses autocomplete to select a boss.
    - This command displays the drops and their corresponding points for the specified boss.
    - If the boss has an associated image, it will be included as a thumbnail.
    - If there are too many drops to fit in a single embed, the drops will be split into multiple embeds.
    - If the boss is not found, an error message will be sent.
    - If no drops are found for the boss, an error message will be sent.
- `/extravaganza_drop`: Enter boss drop for your team.
  - Usage: `/extravaganza_drop event_name:MyExtravaganza team_member_name:@User boss_name:BossName drop_name:DropName`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - `team_member_name` uses autocomplete to select a member of your team.
    - `boss_name` uses autocomplete to select a boss from the available bosses.
    - `drop_name` uses autocomplete to select a drop from the selected boss's drops.
    - This command allows you to enter a boss drop for your team.
    - You must be a member of a team in the specified event to use this command.
    - The command will return an error message if you are not on a team, or if the selected team member is not on your team.
    - It provides feedback on the original points, added points, and the new total points for the team.
    - It will return an error message if the event, team member, boss, or drop is not found.
- `/extravaganza_drop_remove`: Remove a boss drop.
  - Usage: `/extravaganza_drop_remove event_name:MyExtravaganza team_member_name:@User boss_name:BossName drop_name:DropName`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - `team_member_name` uses autocomplete to select a member of your team that has registered drops.
    - `boss_name` uses autocomplete to select a boss from the available bosses that the team member has drops registered for.
    - `drop_name` uses autocomplete to select a drop from the selected boss's drops that the team member has registered.
    - This command allows team leaders to remove a boss drop entered by a team member.
    - You must be a team leader in the specified event to use this command.
    - The command will return an error message if you are not a team leader, or if the selected team member is not on your team.
    - It provides feedback on the original points, removed points, and the new total points for the team.
    - It will return an error message if the event, team member, boss, or drop is not found.
- `/extravaganza_player_points_all`: Get total points for each player in an event, separated by teams with team colors in one message.
  - Usage: `/extravaganza_player_points_all event_name:MyExtravaganza`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - This command displays the total points for each player in the specified event, separated by teams.
    - Each team's points are displayed in a separate embed, using the team's assigned color.
    - If a player's OSRS in-game name is registered, it will be displayed; otherwise, their Discord username will be shown.
    - If the event or game data is not found, an error message will be sent.
    - If no team points data is found, an error message will be sent.
    - If no player points data is found, an error message will be sent.
- `/extravaganza_team_stats_all`: View drop counts and total points for all teams.

  - Usage: `/extravaganza_team_stats_all event_name:MyExtravaganza`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - This command displays the drop counts and total points for all teams in the specified event.
    - Each team's stats are displayed in a separate embed, using the team's assigned color.
    - It also displays the current leaderboard, showing the top three teams and their points.
    - If the event or game data is not found, an error message will be sent.
    - If no team stats are available, an error message will be sent.
    - If no teams have any points, a message will be displayed indicating that no team is currently leading.

- `/extravaganza_team_stats`: View drop counts and total points for your team or a specified team.
  - Usage: `/extravaganza_team_stats event_name:MyExtravaganza team_name:TeamName` or `/extravaganza_team_stats event_name:MyExtravaganza`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - `team_name` uses autocomplete to select a team within the specified event. If not provided, it defaults to the user's team.
    - This command displays the drop counts and total points for the specified team.
    - If `team_name` is not provided, the command will attempt to determine the user's team.
    - If the user is not in a team, or if the team or event is not found, an error message will be sent.
    - The team's stats are displayed in an embed, using the team's assigned color.
- `/help`: Displays a list of available commands.
  - Usage: `/help`
  - Note:
    - This command displays a list of all available commands, separated into general commands, team leader/admin commands, and admin-only commands.
    - Admin-only commands are only displayed if the user has administrator permissions.
    - The command list is paginated into multiple embeds if there are too many commands.
    - All help messages are sent ephemerally (only visible to the user).

### Team Leader/Admin Commands

- `/event_free_agents_view`: View free agents for a specific event (team leaders and admins).
  - Usage: `/event_free_agents_view event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select an event that has free agents.
    - This command displays a list of free agents for the specified event.
    - Only team leaders and admins are authorized to use this command.
    - If you are not authorized, an error message will be sent.
    - If the event does not exist or there are no free agents, a message indicating this will be sent.
- `/event_teams_view`: View teams and members for a specific event (team leaders and admins).
  - Usage: `/event_teams_view event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select an event that has teams.
    - This command displays a list of teams and their members for the specified event.
    - Only team leaders and admins are authorized to use this command.
    - If you are not authorized, an error message will be sent.
    - If the event does not exist or there are no teams, a message indicating this will be sent.
    - The command displays each team in a separate embed, showing the team's leaders and members.
    - Each team's embed uses the team's assigned color.
- `/team_assign`: Add a member to a team (team leaders and admins).

  - Usage: `/team_assign event_name:MyEvent team_name:TeamName free_agent_osrs_ign:IGN1 team_role:member`
  - Note:
    - `event_name` uses autocomplete to select an event.
    - `team_name` uses autocomplete to select a team within the selected event.
    - `free_agent_osrs_ign` uses autocomplete to select an OSRS in-game name from the free agent pool.
    - `team_role` uses choices to select "leader" or "member".
    - This command assigns a free agent to a team within an event.
    - Only admins and team leaders of the specified team are authorized to use this command.
    - If you are not authorized, an error message will be sent.
    - If the event, team, or free agent is not found, an error message will be sent.
    - After successful assignment, the free agent is removed from the free agent pool.
    - The command sends an embed confirming the assignment.

- `/team_unassign`: Un-add a member to a team and move them back to the free agent pool (team leaders and admins).
  - Usage: `/team_unassign member_ign:IGN1 event_name:MyEvent`
  - Note:
    - `member_ign` uses autocomplete to select an OSRS in-game name that is currently a member of a team.
    - `event_name` uses autocomplete to select an event that the member is in.
    - This command removes a member from their team and moves them back to the free agent pool for the specified event.
    - Only admins and team leaders are authorized to use this command.
    - If you are not authorized, an error message will be sent.
    - If the event or member is not found, an error message will be sent.
    - After successful unassignment, the member is added back to the free agent pool.

### Admin-Only Commands

- `/admin_event_create`: Admin: Create a new event.
  - Usage: `/admin_event_create event_name:MyUniqueEvent event_type:bingo event_date:2024-12-25 event_time:02:00 PM CST`
  - Note:
    - `event_name` must be a unique name for the event.
    - `event_type` uses autocomplete to suggest event types like "bingo," "snakes_ladders," or "extravaganza."
    - `event_date` must be in YYYY-MM-DD format.
    - `event_time` must be in 12-hour format with AM or PM and include "CST" for Central Standard Time.
- `/admin_event_delete`: Admin: Delete an existing event.
  - Usage: `/admin_event_delete event_name:MyUniqueEvent`
  - Note:
    - `event_name` uses autocomplete to select the event to delete.
    - This command will also delete associated game data, teams, and free agents.
- `/admin_regenerate_board`: Admin: Regenerate the game board for an event.
  - Usage: `/admin_regenerate_board event_name:MyUniqueEvent`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - This command will regenerate the game board for the selected event.
    - A confirmation prompt will appear before the board is regenerated.
- `/admin_member_join`: Admin: Add OSRS names for a user.
  - Usage: `/admin_member_join discord_user:@User osrs_igns:IGN1, IGN2, IGN3`
  - Note:
    - `discord_user` is a Discord user mention (e.g., `@User`).
    - `osrs_igns` is a comma-separated list of Old School RuneScape in-game names.
    - If the user has already registered their OSRS names, use `/admin_member_update` instead.
- `/admin_member_update`: Admin: Update OSRS names for a user.
  - Usage: `/admin_member_update discord_user:@User osrs_igns:IGN1, IGN2, IGN3`
  - Note:
    - `discord_user` is a Discord user mention (e.g., `@User`).
    - `osrs_igns` is a comma-separated list of Old School RuneScape in-game names.
    - If the user has not registered their OSRS names yet, use `/admin_member_join` instead.
- `/admin_members_view`: Admin: View all members and their OSRS names.
  - Usage: `/admin_members_view`
  - Note:
    - This command displays a list of all registered Discord users and their associated Old School RuneScape in-game names.
    - If no member data exists, a message indicating this will be sent.
- `/admin_event_join`: Admin: Join a user to an event as a free agent.
  - Usage: `/admin_event_join event_name:MyEvent member_name:@User selected_character:IGN1`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - `member_name` uses autocomplete to select a Discord user who is not already in the event.
    - `selected_character` uses autocomplete to select an OSRS in-game name associated with the user.
    - The user must have registered their OSRS names using `/admin_member_join` before they can be added to an event.
    - If the user is already a free agent for the event, a message will be sent indicating this.
- `/admin_event_unjoin`: Admin: Remove a user from an event's free agent pool.
  - Usage: `/admin_event_unjoin event_name:MyEvent member_osrs_ign:IGN1`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - `member_osrs_ign` uses autocomplete to select an OSRS in-game name that is currently in the event's free agent pool.
    - If the OSRS in-game name is not a free agent for the event, a message will be sent indicating this.
- `/admin_team_create`: Admin: Create a new team for an event.
  - Usage: `/admin_team_create event_name:MyEvent team_name:TeamName team_color:#FF0000`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - `team_name` is the name of the new team.
    - `team_color` must be a 6-character hex color code (e.g., `#FF0000` for red).
    - The team name must be unique within the event.
    - If the event is a "snakes_ladders" event, a pawn position will be initialized for the team.
- `/admin_team_delete`: Admin: Delete a team from an event.
  - Usage: `/admin_team_delete event_name:MyEvent team_name:TeamName`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - `team_name` uses autocomplete to select the team to delete.
    - The team must exist within the specified event.
    - Move members in the team back into the free agents pool.
    - If the event is a "snakes_ladders" event, the team's pawn position will be removed.
- `/admin_team_role_change`: Admin: Change the role of a member in a team.
  - Usage: `/admin_team_role_change event_name:MyEvent member_ign:IGN1 new_role:leader`
  - Note:
    - `event_name` uses autocomplete to select the event.
    - `member_ign` uses autocomplete to select an OSRS in-game name that is currently a member of a team in the event.
    - `new_role` uses autocomplete to suggest "leader" or "member".
    - This command changes the role of the specified member within their team for the given event.
    - If the member is not found in any team for the event, an error message will be sent.
- `/admin_boss_drops_showall`: Admin: Shows all boss drops and points in embeds.
  - Usage: `/admin_boss_drops_showall`
  - Note:
    - This command displays all boss drops and their associated points in a series of embeds.
    - Each boss's drops are shown in a separate embed.
    - If a boss has an associated image, it will be included as a thumbnail.
    - If a boss has more than 25 drops, a warning will be added to the embed, and some drops may not be shown.
    - If no boss drops are found, a message indicating this will be sent.
- `/admin_boss_drop_edit`: Admin: Edit boss drop points.
  - Usage: `/admin_boss_drop_edit boss_name: <boss_name> drop_name: <drop_name> points: <points>`
  - Note:
    - This command allows administrators to edit the point value of a specific boss drop.
    - It requires the boss name, drop name, and the new point value as input.
    - It will display the previous point value and the new point value in the confirmation message.
    - It will return an error if the boss or drop does not exist.
- `/admin_boss_drop_add`: Admin: Add a new boss drop.
  - Usage: `/admin_boss_drop_add boss_name: <boss_name> drop_name: <drop_name> points: <points>`
  - Note:
    - This command allows administrators to add a new drop to a boss or update the points of an existing drop.
    - It requires the boss name, drop name, and the point value as input.
    - If the drop already exists, it will update the points and display the previous and new point values.
    - If the drop is new, it will add the drop and display a confirmation message.
    - It will return an error if the boss does not exist.
- `/admin_boss_drop_remove`: Admin: Remove a boss drop.
  - Usage: `/admin_boss_drop_remove boss_name: <boss_name> drop_name: <drop_name>`
  - Note:
    - This command allows administrators to remove a specific drop from a boss.
    - It requires the boss name and drop name as input.
    - It will prompt the user for confirmation before removing the drop.
    - It will return an error if the boss or drop does not exist.
- `/admin_extravaganza_drop`: Admin: Help a member add a drop to their team.
  - Usage: `/admin_extravaganza_drop event_name:MyExtravaganza team_name:TeamName team_member_name:@User boss_name:BossName drop_name:DropName`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - `team_name` uses autocomplete to select a team within the selected event.
    - `team_member_name` uses autocomplete to select a member of the selected team.
    - `boss_name` uses autocomplete to select a boss from the available bosses.
    - `drop_name` uses autocomplete to select a drop from the selected boss's drops.
    - This command allows an admin to add a drop to a specific team member's drop log for an extravaganza event.
    - It provides feedback on the original points, added points, and the new total points for the team.
    - It will return an error message if the event, team, member, boss, or drop is not found or if the event is not an extravaganza.
- `/admin_extravaganza_drop_remove`: Admin: Remove a drop from a team.
  - Usage: `/admin_extravaganza_drop_remove event_name:MyExtravaganza team_name:TeamName team_member_name:@User boss_name:BossName drop_name:DropName`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - `team_name` uses autocomplete to select a team within the selected event that has drops recorded.
    - `team_member_name` uses autocomplete to select a member of the selected team who has drops recorded.
    - `boss_name` uses autocomplete to select a boss from the team's recorded drops.
    - `drop_name` uses autocomplete to select a drop from the selected boss's drops that the team member has recorded.
    - This command allows an admin to remove a specific drop from a team member's drop log for an extravaganza event.
    - It provides feedback on the original points, removed points, and the new total points for the team.
    - It will return an error message if the event, team, member, boss, or drop is not found or if the team member does not have that drop recorded.
- `/admin_extravaganza_leaderboard`: Admin: Shows the team leaderboard and graph.
  - Usage: `/admin_extravaganza_leaderboard event_name:MyExtravaganza`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - This command generates and sends the team leaderboard and a graph of team scores for the specified extravaganza event.
    - It forces an immediate update of the leaderboard and graph.
    - If the event is not found or the game ID is missing, an error message will be sent.
    - If any other error occurs during the process, an error message will be sent.
- `/admin_extravaganza_reset_data`: Admin: Reset team drop counts and total points for an extravaganza event.
  - Usage: `/admin_extravaganza_reset_data event_name:MyExtravaganza`
  - Note:
    - `event_name` uses autocomplete to select an extravaganza event.
    - This command resets the team drop counts and total points for the specified extravaganza event.
    - A confirmation prompt will appear before the data is reset.
    - If the event is not found or the game ID is missing, an error message will be sent.
- `/admin_schedule_event_tasks`: Admin: Schedules tasks for an event.
  - Usage: `/admin_schedule_event_tasks event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select an event.
    - This command schedules tasks for the specified event.
    - Currently, only extravaganza events support scheduled tasks.
    - If the event is an extravaganza event, it will schedule the necessary tasks and send a confirmation message.
    - If the event is a bingo or snakes_ladders event, a message indicating that scheduled tasks are not yet implemented will be sent.
    - If the event type is not supported, an error message will be sent.
    - If the event is not found or the game ID is missing, an error message will be sent.
    - If the extravaganza tasks are already scheduled, a message indicating this will be sent.
- `/admin_remove_scheduled_task`: Admin: Removes a scheduled task for an event.
  - Usage: `/admin_remove_scheduled_task event_name:MyEvent`
  - Note:
    - `event_name` uses autocomplete to select an event with scheduled tasks.
    - This command removes scheduled tasks for the specified event.
    - Currently, only extravaganza events support scheduled tasks.
    - If the event is an extravaganza event and tasks were scheduled, it will remove the tasks and send a confirmation message.
    - If the event is an extravaganza event and tasks were not scheduled, a message indicating this will be sent.
    - If the event is a bingo or snakes_ladders event, a message indicating that scheduled tasks are not yet implemented will be sent.
    - If the event type is not supported, an error message will be sent.
    - If the event is not found or the game ID is missing, an error message will be sent.

## Event Management

### Creating Events

Use the `/create_event` command to create a new event. Follow the prompts to provide event details.

### Tracking Drops

Users can submit drop logs using the `/submit_drop` command. The bot will automatically calculate team scores.

## Support

For support, please contact @smacksmackk on Discord.
