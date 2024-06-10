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
        super().__init__((self.convert_state_to_search_state(initial),
                          self.player_position(initial)))
        self.m, self.n = len(initial), max([len(row) for row in initial])
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.solution_node = None

    @staticmethod
    def player_position(state):
        for i, row in enumerate(state):
            for j, cell in enumerate(row):
                if '@' in cell:
                    return i, j

    @staticmethod
    def convert_state_to_search_state(state):
        search_state = []
        for row in state:
            search_row = []
            for cell in row:
                search_cell = [cell]
                if cell in ["@", "$"]:
                    search_cell.append(" ")
                search_row.append(tuple(search_cell))
            search_state.append(tuple(search_row))
        return tuple(search_state)

    @staticmethod
    def state_to_tuple(state):
        return tuple([tuple([tuple(cell) for cell in row]) for row in state])

    @staticmethod
    def state_to_list(state):
        return [[list(cell) for cell in row] for row in state]

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        player_i, player_j = state[1]
        possible_actions = []
        for di, dj in self.directions:
            new_i, new_j = player_i + di, player_j + dj
            if 0 <= new_i < self.m and 0 <= new_j < len(state[0][new_i]) and state[0][new_i][new_j] != "#":
                if len(state[0][new_i][new_j]) == 1 and (" " in state[0][new_i][new_j] or
                                                         "." in state[0][new_i][new_j]):
                    possible_actions.append((di, dj))
                if ("$" in state[0][new_i][new_j] and
                        0 <= new_i + di < self.m and 0 <= new_j + dj < len(state[0][new_i]) and
                        "$" not in state[0][new_i + di][new_j + dj] and
                        "#" not in state[0][new_i + di][new_j + dj]):
                    possible_actions.append((di, dj))

        return possible_actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        player_i, player_j = state[1]
        di, dj = action
        new_i, new_j = player_i + di, player_j + dj

        new_state = self.state_to_list(state[0])

        new_state[player_i][player_j].remove("@")
        if "$" in new_state[new_i][new_j]:
            new_state[new_i][new_j].remove("$")
            new_state[new_i + di][new_j + dj].append("$")
        new_state[new_i][new_j].append("@")

        return self.state_to_tuple(new_state), (new_i, new_j)

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        return len(SokobanSolver.get_unplaced_crate_locations(state)) == 0

    @staticmethod
    def get_unplaced_crate_locations(state):
        unplaced_crates = []
        for i, row in enumerate(state[0]):
            for j, cell in enumerate(row):
                if "." in cell and "$" not in cell:
                    unplaced_crates.append((i, j))
        return unplaced_crates

    @staticmethod
    def get_empty_storage_place_locations(state):
        empty_storage_places = []
        for i, row in enumerate(state[0]):
            for j, cell in enumerate(row):
                if "$" in cell and "." not in cell:
                    empty_storage_places.append((i, j))
        return empty_storage_places

    @staticmethod
    def manhattan_distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def h(node):
        """Return the heuristic value for a given state. Default is 0."""
        unplaced_crate_locations = SokobanSolver.get_unplaced_crate_locations(node.state)
        empty_storage_place_locations = SokobanSolver.get_empty_storage_place_locations(node.state)
        value = 0

        for crate_location in unplaced_crate_locations:
            for storage_place_location in empty_storage_place_locations:
                value += SokobanSolver.manhattan_distance(crate_location, storage_place_location)
        value /= len(unplaced_crate_locations) if len(unplaced_crate_locations) > 0 else 1
        value += min([SokobanSolver.manhattan_distance(node.state[1], unplaced_crate_location)
                     for unplaced_crate_location in unplaced_crate_locations]) - 1 if len(unplaced_crate_locations) > 0 else 1

        return value

    def solve(self):
        self.solution_node = astar_search(self, h=self.h)
        return self.solution_node is not None

    def solution(self):
        return self.solution_node.solution() if self.solution_node else None

