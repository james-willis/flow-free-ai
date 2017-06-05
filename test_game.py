import pytest
from game import Dot, GameInstance, _Tile

class TestTile(object):
	tile1 = _Tile()
	tile2 = _Tile()
	tile3 = _Tile()

	tile1.next = tile2
	tile2.next = tile3

	def test_end_returns_self(self):
		assert self.tile3.line_end() == self.tile3

	def test_follow_one_link(self):
		assert self.tile2.line_end() == self.tile3

	def test_follow_multi_link(self):
		assert self.tile1.line_end() == self.tile3

class TestGameInstance(object):
	valid_dots = [Dot(1, 1, 'blue'), Dot(2, 2, 'red'), Dot(3, 3, 'blue'), Dot(0, 0, 'red')]
	colliding_dots = valid_dots[1:] + [Dot(2, 2, 'blue')]
	no_matching_dot = valid_dots[:-1]
	
	dim = 5

	def test_valid_game_board(self):
		game = GameInstance(self.dim, self.valid_dots)
		assert isinstance(game, GameInstance)
		assert len(game.board) == self.dim
		assert len(game.board[0]) == self.dim
		for dot in self.valid_dots:
			tile = game.board[dot.x][dot.y]
			assert tile.is_dot
			assert dot.color == tile.color

	def test_invalid_game_boards(self):
		with pytest.raises(ValueError):
			GameInstance(self.dim, self.colliding_dots)
		with pytest.raises(ValueError):
			GameInstance(self.dim, self.no_matching_dot)

	def test_valid_color_tile(self):
		game = GameInstance(self.dim, self.valid_dots)

		# tile at (1,1) is a blue dot
		game.color_tile((1, 1), (1, 2))
		assert game.board[1][2].color == 'blue'
		assert game.board[1][1].next == game.board[1][2]
		assert not game.board[1][2].next

		game.color_tile((1, 2), (1, 3))
		assert game.board[1][2].next == game.board[1][3]
		assert game.board[1][3].color == 'blue'
		assert not game.board[1][3].next
		game.color_tile((1, 3), (2, 3))

		# finish the flow
		game.color_tile((2, 3), (3, 3))
		assert game.board[3][3].color == 'blue'
		assert game.board[2][3].next == game.board[3][3]
		assert game.board[1][1].line_end() == game.board[3][3]

		#interrupt another flow
		game.color_tile((2, 2), (1, 2))
		assert game.board[1][2].color == 'red'
		assert not game.board[1][2].next
		assert game.board[1][1].line_end() == game.board[1][1]
		assert not game.board[1][3].next

	def test_invalid_color_tile(self):
		game = GameInstance(self.dim, self.valid_dots)
		game.color_tile((1, 1), (1, 2))

		# write on wrong colored dot
		with pytest.raises(ValueError):
			game.color_tile((1, 2), (2, 2))

		# terminate at starting dot
		with pytest.raises(ValueError):
			game.color_tile((1, 2), (1, 1))

		# draw off the game board
		with pytest.raises(IndexError):
			game.color_tile((0, 0), (-1, 0))

		# draw nonadjacent tile
		with pytest.raises(ValueError):
			game.color_tile((0, 0), (1, 1))

		# draw tile not from end of line
		with pytest.raises(ValueError):
			game.color_tile((1, 1), (0, 1))

	def test_remove_line(self):
		game = GameInstance(self.dim, self.valid_dots)
		game.remove_line((1, 1))
		assert game.board[1][1].line_end() == game.board[1][1]

		game.board[1][1].next = game.board[1][2]
		game.board[1][2].color = 'blue'
		game.board[1][2].next = game.board[1][3]
		game.board[1][3].color = 'blue'
		game.remove_line((1, 1))
		assert game.board[1][1].line_end() == game.board[1][1]

		game.board[1][1].next = game.board[1][2]
		game.board[1][2].color = 'blue'
		game.board[1][2].next = game.board[1][3]
		game.board[1][3].color = 'blue'
		game.remove_line((1, 2))
		assert game.board[1][1].line_end() == game.board[1][2]

	def test_previous(self):
		game = GameInstance(self.dim, self.valid_dots)
		game.board[1][1].next = game.board[1][2]
		game.board[1][2].color = 'blue'
		game.board[1][2].next = game.board[1][3]
		game.board[1][3].color = 'blue'
		game.board[2][3].color = 'blue'
		assert game._previous((1,3)) == (1,2)
		assert game._previous((1,2)) == (1,1)
		assert game._previous((1,1)) == None
		assert game._previous((2,3)) == None

	def test_won(self):
		winnable_dots = [Dot(0, 0, 'green'), Dot(3, 3, 'green'),
						 Dot(1, 0, 'yellow'), Dot(3, 0, 'yellow'),
						 Dot(4, 0, 'orange'), Dot(2, 2, 'orange'),
						 Dot(0, 2, 'red'), Dot(3, 4, 'red'),
						 Dot(3, 2, 'blue'), Dot(4, 4, 'blue')]
		game = GameInstance(self.dim, winnable_dots)
		assert not game.game_won()

		# green
		game.color_tile((0, 0), (0, 1))
		game.color_tile((0, 1), (1, 1))
		game.color_tile((1, 1), (1, 2))
		game.color_tile((1, 2), (1, 3))
		game.color_tile((1, 3), (2, 3))
		game.color_tile((2, 3), (3, 3))
		assert not game.game_won()

		# yellow
		game.color_tile((1, 0), (2, 0))
		game.color_tile((2, 0), (3, 0))
		assert not game.game_won()

		# orange
		game.color_tile((4, 0), (4, 1))
		game.color_tile((4, 1), (3, 1))
		game.color_tile((3, 1), (2, 1))
		game.color_tile((2, 1), (2, 2))
		assert not game.game_won()

		# blue
		game.color_tile((3, 2), (4, 2))
		game.color_tile((4, 2), (4, 3))
		game.color_tile((4, 3), (4, 4))
		assert not game.game_won()

		# red 
		game.color_tile((0, 2), (0, 3))
		game.color_tile((0, 3), (0, 4))
		game.color_tile((0, 4), (1, 4))
		game.color_tile((1, 4), (2, 4))
		game.color_tile((2, 4), (3, 4))
		assert  game.game_won()
