class GameInstance(object):
    """
    A instance of a game of Flow Free
    designed for an AI to play
    """
    def __init__(self, dim, dots):
        self.board = [[self.Tile()] * dim for _ in range(dim)]
        self.dots = dots
        self.dim = dim

        for dot in dots:
            self.board[dot.x][dot.y] = self.Tile(True, dot.color)

    class Tile(object):
        def __init__(self, is_dot=False, color=None):
            self.is_dot = is_dot
            self.color = color
            self.next = None

    class Dot(object):
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.color = color

    def color_tile(self, previous, current):
        """
        updates the gameboard to add a valid tile to a path
        """
        previous_tile = self.board[previous[0]][previous[1]]
        current_tile = self.board[current[0]][current[1]]

        for dim in previous + current:
            if not 0 <= dim < self.dim:
                raise IndexError("Previous and current tiles must be within dimensions of\
                    gameboard")

        if current_tile.is_dot:
            raise ValueError("Cannot draw on dot")

        if  previous_tile.next:
            raise ValueError("Previous tile must be the end of line")

        if not previous_tile.color:
            raise ValueError("Previous tile must be part of a line")

        if abs(current[0] - previous[0]) + abs(current[1] - previous[1]) != 1:
            raise ValueError("New tile must be adjacent to previous tile")

        # if the theres already a line here, delete all the lines of that color
        if current_tile.color:
            for dot in self.dots:
                if dot.color == current_tile.color:
                    self.remove_line(dot)


        previous_tile.next = current_tile
        current_tile.color = previous_tile.color

    def remove_line(self, origin):
        """
        removes a valid line drawn by a player. line must start from a dot
        """
        current_tile = self.board[origin[0]][origin[1]]

        if not current_tile.is_dot:
            raise ValueError("origin must be a dot")

        # nothing needs to be done to dot
        current_tile = current_tile.next

        # remove color of all non dot tiles in line
        while current_tile.color and not current_tile.is_dot:
            temp = current_tile.next
            current_tile.color = None
            current_tile.next = None
            current_tile = temp

    def game_won(self):
        """

        """
        raise NotImplementedError