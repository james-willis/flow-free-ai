"""Represent a game of Flow Free.

This module is designed to represent an instance of the game Flow Free, Flow Free is a mobile game
created by Big Duck Games, and is available on iOS and Android devices. This modules attempts to
replicate the behavior of the game as closely as possible, and is designed with human and AI
players in mind.

"""

class _Tile(object):
    """A tile to represent a single position on a Flow Free board.

    Attributes:
        is_dot (boolean): Indicates if the tile contains a dot.
        color (str): Indicates the color of the tile.
        next (:obj:`tile`): The next tile in line.  Is None if no next item in line.

    """
    def __init__(self, is_dot=False, color=None):
        self.is_dot = is_dot
        self.color = color
        self.next = None

    def line_end(self):
        """returns the tile at the terminus of the line by following the next values"""
        curr = self
        while curr.next:
            curr = curr.next
        return curr

class _Dot(object):
    """Represent a dot on the gameboard.

    Attributes:
        x (int): the x coordinate of the location of the dot on the gameboard.
        y (int): the y coordinate of the location of the dot on the gameboard.
        color (str): the color of the dot, there will be exactly two dots of each color on a
            given board.
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class GameInstance(object):

    """Represent a game of Flow Free and the behaviors required to play the game.

    Attributes:
        dim (int): the dimension of the gameboard.
        board (:obj:`list` of  :obj:`tile`): A two dimensional (dim x dim) list of the tiles that
            comprise the gameboard.
        dots (:obj:`list` of :obj:`dots`): A list of all of the dots on the gameboard.

    """

    def __init__(self, dim, dots):
        self.board = [[_Tile()] * dim for _ in range(dim)]
        self.dots = dots
        self.dim = dim

        for dot in dots:
            self.board[dot.x][dot.y] = _Tile(True, dot.color)

    def color_tile(self, previous, current):
        """Updates the gameboard to add a tile to a path.

        Args:
            previous (:obj:`tuple` of :obj:`int`): a tuple of the location of the end of the line
                you'd like to expand. The first element is the x coordinate and the second element
                is the y coordinate.
            current (:obj:`tuple` of :obj:`int`): a tuple of the location of tile to add to the
                line. The first element is the x coordinate and the second element is the y
                coordinate.
        Raises:
            IndexError: If either of the args is outside the bounds of the gameboard.
            ValueError: If the tile to be colored is not at the end of a line, is a dot of a
                different color from the line, or is the tile the line starts from.
        """
        previous_tile = self.board[previous[0]][previous[1]]
        current_tile = self.board[current[0]][current[1]]

        for dim in previous + current:
            if not 0 <= dim < self.dim:
                raise IndexError("Previous and current tiles must be within dimensions of\
                    gameboard")

        if current_tile.is_dot and previous_tile.color != current_tile.color:
            raise ValueError("Cannot draw on dot")

        if current_tile.is_dot and current_tile.next:
            # If the dot has a next value then it must be the same dot the line starts from since
            # 2 lines of the same color cannot exist.
            raise ValueError("cannot start and end line at same dot")

        if  previous_tile.next:
            raise ValueError("Previous tile must be the end of line")

        if not previous_tile.color:
            raise ValueError("Previous tile must be part of a line")

        if abs(current[0] - previous[0]) + abs(current[1] - previous[1]) != 1:
            raise ValueError("New tile must be adjacent to previous tile")

        # If starting a new line, delete line from other dot of same color.
        if previous_tile.is_dot:
            other_dot = None
            for dot in self.dots:
                # If its the other dot of the same color.
                if dot.x != previous[0] and dot.y != previous[1] and dot.color == previous.color:
                    other_dot = dot
            self.remove_line((other_dot.x, other_dot.y))

        # If theres already a line here, delete the existing line from current tile.
        if current_tile.color:
            self.remove_line(current)


        previous_tile.next = current_tile
        current_tile.color = previous_tile.color

    def remove_line(self, origin):
        """Remove a line drawn from the gameboard.

        The path is removed from the provided origin argument and delete the line following the
        linked list of `next ` values until a dot is encountered or  the line ends.

        Args:
            origin (:obj:`tuple` of :obj:`int`): a tuple of the location of the tile to begin line
                removal from. The first element is the x coordinate and the second element is the y
                coordinate.
        """
        current_tile = self.board[origin[0]][origin[1]]

        if current_tile.is_dot:
            temp = current_tile.next
            current_tile.next = None
            current_tile = temp

        # Remove color of all non dot tiles in line.
        while current_tile and current_tile.color and not current_tile.is_dot:
            temp = current_tile.next
            current_tile.color = None
            current_tile.next = None
            current_tile = temp

    def game_won(self):
        """Determine if the current board is a winning configuration.

        A winning configuration means that all dots are connected via lines to their pair (other dot
        of the same color) and all tiles have a color.

        Return:
            True if the board is a winning configuration, False otherwise.
        """

        # Makes sure every tile is colored
        for column in self.board:
            for tile in column:
                if not tile.color:
                    return False

        # Makes sure each color has a line.
        colors = set()
        for dot in self.dots:
            dot_tile = self.board[dot.x][dot.y]
            colors += dot.color
        for dot in self.dots:
            dot_tile = self.board[dot.x][dot.y]
            # If we've already found a line for this color.
            if dot.color not in colors:
                continue
            # If this dot starts a line and ends at the other dot.
            if dot_tile.next and not dot_tile.line_end().is_dot:
                return False
            elif dot_tile.next:
                colors.remove(dot.color)
        # If colors isn't empty, not all colors have lines.
        return not colors
