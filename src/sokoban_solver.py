from src.search import Problem, astar_search


class SokobanSolver(Problem):
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial):
        """The constructor specifies tdhe initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        super().__init__(initial, self.player_position(initial))
        self.m, self.n = len(initial), len(initial[0])
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.solution_node = None

    @staticmethod
    def player_position(state):
        for i, row in enumerate(state):
            for j, cell in enumerate(row):
                if cell == '@':
                    return i, j

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        player_i, player_j = state[1]
        possible_actions = []
        for di, dj in self.directions:
            new_i, new_j = player_i + di, player_j + dj
            if 0 <= new_i < self.m and 0 <= new_j < self.n and state[0][new_i][new_j] != "#":
                if state[0][new_i][new_j] == "." and state[0][new_i + di][new_j + dj] not in [".", "#"]:
                    possible_actions.append((di, dj))

        return possible_actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        raise NotImplementedError

    def h(self, node):
        """Return the heuristic value for a given state. Default is 0."""
        return 0

    def solve(self):
        self.solution_node = astar_search(self)
        return self.solution_node is not None

    def solution(self):
        return self.solution_node.solution() if self.solution_node else None

