# Welcome to the Shadeauxband Events Bot Tutorial!

Hey everyone! This tutorial will guide you through using our awesome new Shadeauxband Events Bot. This bot helps us manage events, track drop logs, and keep team scores organized. Let's get started!

**Understanding the Data Flow:**

Before diving into commands, let's understand how the bot organizes information:

> 1.  **Members:**
>     - Users register their Discord account and OSRS in-game names using `/join` or `/admin_member_join`.
>     - This creates a member profile, linking Discord to OSRS accounts.
> 2.  **Event Free Agents:**
>     - Members can join events as free agents using `/join_event` or `/admin_event_join`.
>     - Free agents are available for team leaders to assign to teams.
> 3.  **Teams:**
>     - Teams are created by admins using `/admin_team_create`.
>     - Team leaders and admins assign members to teams using `/team_assign`.
>     - Teams participate in events and their scores are tracked.
> 4.  **Events:**
>     - Events are created by admins using `/admin_event_create`.
>     - Events have a type (bingo, snakes_ladders, extravaganza) and a schedule.
>     - Events contain free agents and teams.
> 5.  **Games:**
>     - Games are created as part of the event creation.
>     - Games contain the game data, such as bingo boards, snakes and ladders positions, or extravaganza drop logs.

Now, let's get into the commands:

### 1. Adding Your OSRS In-Game Names:

Before you can join any events, you need to tell the bot your Old School RuneScape (OSRS) in-game names.

> - **Command:** `/join osrs_igns:IGN1, IGN2, IGN3`
> - **Example:** `/join osrs_igns:IronSmitty, PureChad, RangeTank`
> - **How:**
>   - Type `/join` in any channel the bot can see.
>   - Replace `IGN1, IGN2, IGN3` with your actual OSRS names, separated by commas.
>   - Press Enter.
> - **Why:** This links your Discord account to your OSRS names, making it easy to track your progress in events.

### 2. Joining an Event:

To participate in an event as a free agent (someone not yet on a team), you'll use this command:

> - **Command:** `/join_event event_name:MyEvent selected_character:IGN1`
> - **Example:** `/join_event event_name:BossingExtravaganza selected_character:IronSmitty`
> - **How:**
>   - Type `/join_event`.
>   - Use the autocomplete feature to select the `event_name` you want to join.
>   - Use the autocomplete to select the `selected_character` (one of your registered OSRS names).
>   - Press Enter.
> - **Note:** You must have used `/join` to register your OSRS names first!

### 3. Viewing Event Information:

> - **Free Agents:** Team leaders and admins can use `/event_free_agents_view event_name:MyEvent` to see who's available to join teams.
> - **Teams:** Team leaders and admins can use `/event_teams_view event_name:MyEvent` to see the teams and their members.

### 4. Team Management (Team Leaders and Admins):

> - **Editing Team:** Team leaders and admins can use `/team_edit event_name:MyEvent old_team_name:TeamA new_team_name:TeamB new_team_color:#00FF00` to edit a team's name and color within an event.
> - **Assigning Members:** Team leaders and admins can use `/team_assign event_name:MyEvent team_name:TeamName free_agent_osrs_ign:IGN1 team_role:member` to add free agents to their teams.
> - **Unassigning Members:** Team leaders and admins can use `/team_unassign member_ign:IGN1 event_name:MyEvent` to remove members from teams.
> - **Changing Roles:** Admins can use `/admin_team_role_change event_name:MyEvent member_ign:IGN1 new_role:leader` to change member roles.

### 5. Bingo and Snakes and Ladders Events:

> - **Viewing the Board:** Use `/draw_board event_name:MyEvent` to see the game board.
> - **Viewing Snakes and Ladders Tasks:** Use `/list_snakes_ladders_tasks event_name:MySnakesLaddersEvent` to see the task list and snake/ladder positions.
> - **Rolling Dice (Snakes and Ladders):** Team leaders use `/roll_dice event_name:MySnakesLaddersEvent` to roll the dice and move their team's pawn.
> - **Reverting Rolls (Snakes and Ladders):** Team leaders use `/revert_roll event_name:MySnakesLaddersEvent` to revert their team's last dice roll and move their pawn back to the previous position.
> - **Re-rolling Dice (Snakes and Ladders):** Team leaders use `/reroll event_name:MySnakesLaddersEvent` to revert their team's last dice roll and roll again.

### 6. Extravaganza Events (Drop Logging):

> - **Viewing Boss Drops:** Use `/extravaganza_boss_drops boss_name:BossName` to see the drops and points for a boss.
> - **Entering Drops:** Use `/extravaganza_drop event_name:MyExtravaganza team_member_name:@User boss_name:BossName drop_name:DropName` to enter your team's drops.
> - **Removing Drops:** Team leaders use `/extravaganza_drop_remove event_name:MyExtravaganza team_member_name:@User boss_name:BossName drop_name:DropName` to remove drops.
> - **Viewing Player Points:** Use `/extravaganza_player_points_all event_name:MyExtravaganza` to see player points.
> - **Viewing Team Stats:** Use `/extravaganza_team_stats_all event_name:MyExtravaganza` to see all team stats, or `/extravaganza_team_stats event_name:MyExtravaganza team_name:TeamName` to see a specific team's stats.

### 7. Getting Help:

> - **Command List:** Use `/help` to see a list of all commands.

### Admin-Only Commands (For Admins):

> - **Creating Events:** `/admin_event_create event_name:MyUniqueEvent event_type:bingo event_date:2024-12-25 event_time:02:00 PM CST`
> - **Deleting Events:** `/admin_event_delete event_name:MyUniqueEvent`
> - **Regenerating Boards:** `/admin_regenerate_board event_name:MyUniqueEvent`
> - **Adding Member OSRS Names:** `/admin_member_join discord_user:@User osrs_igns:IGN1, IGN2, IGN3`
> - **Updating Member OSRS Names:** `/admin_member_update discord_user:@User osrs_igns:IGN1, IGN2, IGN3`
> - **Viewing All Members:** `/admin_members_view`
> - **Adding User to Free Agent Pool:** `/admin_event_join event_name:MyEvent member_name:@User selected_character:IGN1`
> - **Removing User from Free Agent Pool:** `/admin_event_unjoin event_name:MyEvent member_osrs_ign:IGN1`
> - **Creating Teams:** `/admin_team_create event_name:MyEvent team_name:TeamName team_color:#FF0000`
> - **Deleting Teams:** `/admin_team_delete event_name:MyEvent team_name:TeamName`
> - **Changing Team Roles:** `/admin_team_role_change event_name:MyEvent member_ign:IGN1 new_role:leader`
> - **Showing All Boss Drops:** `/admin_boss_drops_showall`
> - **Admin Editing Boss Drop Points:** `/admin_boss_drop_edit boss_name:BossName drop_name:DropName points:NewPoints`
> - **Admin Adding Boss Drop:** `/admin_boss_drop_add boss_name:BossName drop_name:DropName points:Points`
> - **Admin Removing Boss Drop:** `/admin_boss_drop_remove boss_name:BossName drop_name:DropName`
> - **Admin Adding Drops:** `/admin_extravaganza_drop event_name:MyExtravaganza team_name:TeamName team_member_name:@User boss_name:BossName drop_name:DropName`
> - **Admin Removing Drops:** `/admin_extravaganza_drop_remove event_name:MyExtravaganza team_name:TeamName team_member_name:@User boss_name:BossName drop_name:DropName`
> - **Generating Leaderboard/Graph:** `/admin_extravaganza_leaderboard event_name:MyExtravaganza`
> - **Resetting Extravaganza Data:** `/admin_extravaganza_reset_data event_name:MyExtravaganza`
> - **Scheduling Event Tasks:** `/admin_schedule_event_tasks event_name:MyEvent`
> - **Removing Scheduled Tasks:** `/admin_remove_scheduled_task event_name:MyEvent`

### Important Notes:

> - Always use the autocomplete feature when available to ensure you're using the correct event, team, or player names.
> - If you encounter any issues or have questions, please reach out to @smacksmackk on Discord.

We hope you enjoy using the Shadeauxband Events Bot! Let the games begin!
