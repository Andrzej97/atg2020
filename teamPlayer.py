import functions as fun
import random

class Player:
    def __init__(self):
        self.id = "Id1"
        self.name = "Coward Player" + str(random.randint(0, 1000))
        self.team = ""
        self.cols_count = 0
        self.rows_count = 0
        self.x = 0
        self.y = 0
        self.tank_direction = fun.S
        self.gun_direction = fun.S
        self.map = ""
        self.my_team_players_names = []
        self.betrayers = set({})

    # Executed at the beginning of the game.
    def set_init_values(self, player_id, team_name, cols_count, rows_count):
        self.id = player_id
        self.team = team_name
        self.cols_count = cols_count
        self.rows_count = rows_count

    # Executed at the beginning to get user name.
    def get_name(self):
        return self.name

    # Executed after killing other player.
    def set_information_about_killing(self):
        pass

    # Executed after tank death.
    def set_information_about_death(self):
        pass

    # Executed when tank had fault. (TANK FAULT RATE is 10% by default)
    def set_information_about_tank_fault(self):
        pass

    # Executed when move was wrong, for example when player wants to move out of map.
    def set_information_about_move_fault(self):
        pass

    # Executed on the end of the game.
    def set_information_about_game_end(self):
        pass

    # Executed at the beginning and after every move. Round kills is list of tuples (killer_name, victim_name).
    def set_map_and_position(self, map, x, y, tank_direction, gun_direction, round, round_kills):
        self.map = map
        self.x = x
        self.y = y
        self.tank_direction = tank_direction
        self.gun_direction = gun_direction
        self.update_betrayers(round_kills)

    def update_betrayers(self, round_kills):
        if len(self.my_team_players_names) == 0:
            self.my_team_players_names = self.get_my_team_players_names()
        for kill in round_kills:
            if kill[1] in self.my_team_players_names and kill[1] not in self.betrayers and kill[0] in self.my_team_players_names:
                self.betrayers.add(kill[0])

    def get_my_team_players_names(self):
        my_team_players_names = []
        players = fun.get_players_from_map(self.map, self.cols_count, self.rows_count)
        for player in players:
            if player[4] == self.team:
                my_team_players_names.append(player[3])
        return my_team_players_names

    # Executed before function get_next_move at the beginning of every round.
    def get_radio_message(self):
        return None

    # Executed at the beginning of every round to get player move.
    def get_next_move(self, radio_messages):
        safe_moves = []

        targeting_current_field = self.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, self.x, self.y)

        # FRONT
        (forward_x, forward_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_FORWARD)
        targeting_forward_field = self.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, forward_x, forward_y)
        is_forward_free = fun.is_free(self.map, forward_x, forward_y, self.cols_count, self.rows_count)

        if targeting_forward_field == 0 and is_forward_free:
            safe_moves.append(fun.MOVE_FORWARD)

        # BACK
        (back_x, back_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_BACK)
        targeting_back_field = self.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, back_x, back_y)
        is_back_free = fun.is_free(self.map, back_x, back_y, self.cols_count, self.rows_count)

        if targeting_back_field == 0 and is_back_free:
            safe_moves.append(fun.MOVE_BACK)

        # Check how many players are targeting me.
        if targeting_current_field > 0:
            # I need to run!
            if len(safe_moves) > 0:
                move = random.choice(safe_moves)
                return (move, 0, 0)

            # LEFT
            (left_x, left_y) = fun.get_coordinates_by_field(self.x, self.y, self.tank_direction, fun.FIELD_ON_THE_LEFT)
            targeting_left_field = self.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, left_x, left_y)
            is_left_free = fun.is_free(self.map, left_x, left_y, self.cols_count, self.rows_count)

            if targeting_left_field == 0 and is_left_free:
                # if the field is free and is safe then turn tank!
                return (fun.TURN_TANK_TO_LEFT, 0, 0)

            # RIGHT
            (right_x, right_y) = fun.get_coordinates_by_field(self.x, self.y, self.tank_direction, fun.FIELD_ON_THE_RIGHT)
            targeting_right_field = self.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, right_x, right_y)
            is_right_free = fun.is_free(self.map, right_x, right_y, self.cols_count, self.rows_count)

            if targeting_right_field == 0 and is_right_free:
                # if the field is free and is safe then turn tank!
                return (fun.TURN_TANK_TO_RIGHT, 0, 0)

            choices = []
            j = random.randint(0, 3)
            step_type = fun.get_move(j)
            choices.append((targeting_current_field, step_type))

            if is_forward_free:
                choices.append((targeting_forward_field, fun.MOVE_FORWARD))
            if is_back_free:
                choices.append((targeting_back_field, fun.MOVE_BACK))
            if is_left_free:
                choices.append((targeting_left_field, fun.TURN_TANK_TO_LEFT))
            if is_right_free:
                choices.append((targeting_right_field, fun.TURN_TANK_TO_RIGHT))

            return (min(choices, key = lambda t: t[0])[1], 0, 0)

        else:
            # I am safe in this round.
            safe_moves.append(fun.TURN_TANK_TO_LEFT)
            safe_moves.append(fun.TURN_TANK_TO_RIGHT)
            safe_moves.append(fun.TURN_GUN_TO_LEFT)
            safe_moves.append(fun.TURN_GUN_TO_RIGHT)

            # Can I shoot someone?
            (to_x, to_y) = fun.get_edge_of_map(self.cols_count, self.rows_count, self.x, self.y, self.gun_direction)
            if self.is_dangerous_player_on_line_of_fire(self.map, self.cols_count, self.rows_count, self.x, self.y, self.gun_direction, to_x, to_y):
                # Yes. Then try to kill him!
                return (fun.SHOOT, to_x, to_y)

            # No, lets check if I can kill someone after turning the gun.
            # First check turning gun to left.
            new_gun_direction = fun.get_gun_direction_after_gun_rotation(self.gun_direction, fun.TURN_GUN_TO_LEFT)
            if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_GUN_TO_LEFT, 0, 0)
            # Now check turning gun to right.
            new_gun_direction = fun.get_gun_direction_after_gun_rotation(self.gun_direction, fun.TURN_GUN_TO_RIGHT)
            if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_GUN_TO_RIGHT, 0, 0)
            # Now check turning tank to right.
            new_gun_direction = fun.get_gun_direction_after_tank_rotation(self.gun_direction,
                                                                          fun.TURN_TANK_TO_RIGHT)
            if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_TANK_TO_RIGHT, 0, 0)
            # Now check turning tank to left.
            new_gun_direction = fun.get_gun_direction_after_tank_rotation(self.gun_direction, fun.TURN_TANK_TO_LEFT)
            if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_TANK_TO_LEFT, 0, 0)
            # Now check going forward
            if fun.MOVE_FORWARD in safe_moves:
                (new_x, new_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_FORWARD)
                if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, new_x, new_y,
                                         self.gun_direction):
                    return (fun.MOVE_FORWARD, 0, 0)
            # Now check going backward
            if fun.MOVE_BACK in safe_moves:
                (new_x, new_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_BACK)
                if self.can_shoot_someone(self.map, self.cols_count, self.rows_count, new_x, new_y,
                                         self.gun_direction):
                    return (fun.MOVE_BACK, 0, 0)

            # Ok, I will not gain anything. Lets turn in random direction.
            return (random.choice(safe_moves), 0, 0)

    def is_betrayer(self, player):
        return player in self.betrayers

    def is_dangerous(self, player_name, player_team):
        return player_team != self.team or self.is_betrayer(player_name)

    def is_dangerous_player_on_line_of_fire(self, map: list, cols_count: int, rows_count: int, from_x: int, from_y: int, gun_direction: str, to_x: int, to_y: int):
        """Check if some dangerous player is on the line of fire"""
        (x_offset, y_offset) = fun.get_offset_in_map(gun_direction)
        next_x = from_x + x_offset
        next_y = from_y + y_offset

        passed_aim = False

        while (not passed_aim) and next_x < cols_count and next_y < rows_count and next_x >= 0 and next_y >= 0:
            if isinstance(map[next_y][next_x], tuple):
                return self.is_dangerous(map[next_y][next_x][1], map[next_y][next_x][2])
            if map[next_y][next_x] == fun.BUILDING_CHAR:
                return False
            if next_x == to_x and next_y == to_y:
                passed_aim = True
            next_x += x_offset
            next_y += y_offset

        return False


    def get_count_of_players_targeting_the_field(self, map: list, cols_count: int, rows_count: int, x: int, y: int):
        """Return count of dangerous players that can shoot at specific field"""
        players = fun.get_players_from_map(map, cols_count, rows_count)
        targeting_players = fun.get_players_targeting_the_field(players, map, cols_count, rows_count, x, y)
        dangerous_targeting_players = list(filter(lambda p: self.is_dangerous(p[3], p[4]), targeting_players))
        return len(dangerous_targeting_players)

    def can_shoot_someone(self, map: list, cols_count: int, rows_count: int, from_x: int, from_y: int, gun_direction: str):
        """Check if from the field player can kill someone."""
        (to_x, to_y) = fun.get_edge_of_map(cols_count, rows_count, from_x, from_y, gun_direction)
        return self.is_dangerous_player_on_line_of_fire(map, cols_count, rows_count, from_x, from_y, gun_direction, to_x, to_y)

