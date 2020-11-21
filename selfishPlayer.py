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

    # Executed before function get_next_move at the beginning of every round.
    def get_radio_message(self):
        return None

    # Executed at the beginning of every round to get player move.
    def get_next_move(self, radio_messages):
        safe_moves = []

        targeting_current_field = fun.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, self.x, self.y)

        # FRONT
        (forward_x, forward_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_FORWARD)
        targeting_forward_field = fun.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, forward_x, forward_y)
        is_forward_free = fun.is_free(self.map, forward_x, forward_y, self.cols_count, self.rows_count)

        if targeting_forward_field == 0 and is_forward_free:
            safe_moves.append(fun.MOVE_FORWARD)

        # BACK
        (back_x, back_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_BACK)
        targeting_back_field = fun.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, back_x, back_y)
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
            targeting_left_field = fun.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, left_x, left_y)
            is_left_free = fun.is_free(self.map, left_x, left_y, self.cols_count, self.rows_count)

            if targeting_left_field == 0 and is_left_free:
                # if the field is free and is safe then turn tank!
                return (fun.TURN_TANK_TO_LEFT, 0, 0)

            # RIGHT
            (right_x, right_y) = fun.get_coordinates_by_field(self.x, self.y, self.tank_direction, fun.FIELD_ON_THE_RIGHT)
            targeting_right_field = fun.get_count_of_players_targeting_the_field(self.map, self.cols_count, self.rows_count, right_x, right_y)
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
            if fun.is_some_player_on_line_of_fire(self.map, self.cols_count, self.rows_count, self.x, self.y, self.gun_direction, to_x, to_y):
                # Yes. Then try to kill him!
                return (fun.SHOOT, to_x, to_y)

            # No, lets check if I can kill someone after turning the gun.
            # First check turning gun to left.
            new_gun_direction = fun.get_gun_direction_after_gun_rotation(self.gun_direction, fun.TURN_GUN_TO_LEFT)
            if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_GUN_TO_LEFT, 0, 0)
            # Now check turning gun to right.
            new_gun_direction = fun.get_gun_direction_after_gun_rotation(self.gun_direction, fun.TURN_GUN_TO_RIGHT)
            if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_GUN_TO_RIGHT, 0, 0)
            # Now check turning tank to right.
            new_gun_direction = fun.get_gun_direction_after_tank_rotation(self.gun_direction, fun.TURN_TANK_TO_RIGHT)
            if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_TANK_TO_RIGHT, 0, 0)
            # Now check turning tank to left.
            new_gun_direction = fun.get_gun_direction_after_tank_rotation(self.gun_direction, fun.TURN_TANK_TO_LEFT)
            if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, self.x, self.y, new_gun_direction):
                return (fun.TURN_TANK_TO_LEFT, 0, 0)
            # Now check going forward
            if fun.MOVE_FORWARD in safe_moves:
                (new_x, new_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_FORWARD)
                if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, new_x, new_y, self.gun_direction):
                    return (fun.MOVE_FORWARD, 0, 0)
            # Now check going backward
            if fun.MOVE_BACK in safe_moves:
                (new_x, new_y) = fun.get_position_after_move(self.x, self.y, self.tank_direction, fun.MOVE_BACK)
                if fun.can_shoot_someone(self.map, self.cols_count, self.rows_count, new_x, new_y, self.gun_direction):
                    return (fun.MOVE_BACK, 0, 0)

            # Ok, I will not gain anything. Lets turn in random direction.
            return (random.choice(safe_moves), 0, 0)
