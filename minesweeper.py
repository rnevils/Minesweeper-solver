import itertools
from typing import Dict, Generator, List, Optional, Set, Tuple


def get_neighbors(board: List[List[Optional[int]]],
                  i: int, j: int) -> List[int]:
    neighbors = []

    height = len(board) - 1
    width = len(board[0]) - 1

    # top left
    if i != 0 and j != 0 and board[i-1][j-1] is None:
        neighbors.append((i-1, j-1))

    # top center
    if i != 0 and board[i-1][j] is None:
        neighbors.append((i-1, j))

    # top right
    if i != 0 and j != width and board[i-1][j+1] is None:
        neighbors.append((i-1, j+1))

    # left
    if j != 0 and board[i][j-1] is None:
        neighbors.append((i, j-1))

    # right
    if j != width and board[i][j+1] is None:
        neighbors.append((i, j+1))

    # botttom left
    if i != height and j != 0 and board[i+1][j-1] is None:
        neighbors.append((i+1, j-1))

    # bottom center
    if i != height and board[i+1][j] is None:
        neighbors.append((i+1, j))

    # bottom right
    if i != height and j != width and board[i+1][j+1] is None:
        neighbors.append((i+1, j+1))

    # convert neighbors into 1d indicies
    return [i*(width+1) + j for i, j in neighbors]


def get_vars(board: List[List[Optional[int]]]
             ) -> Dict[int, List[Dict[int, bool]]]:
    var_map = {}

    # would this be any better by just making it i in range(len(board))
    for i, row in enumerate(board):
        for j, value in enumerate(row):
            if value is not None:

                # get indicies of neighbors that are None
                neighbors = get_neighbors(board, i, j)

                # create permutations -- num_neighbores choose value spots
                mines_layout = [i < value for i in range(len(neighbors))]
                mines_permutations = list(
                    set(itertools.permutations(mines_layout)))

                possible_mine_assignments = [
                    dict(zip(neighbors, values))
                    for values in mines_permutations]

                var_map[i*len(board[0]) + j] = possible_mine_assignments
    return var_map


def get_arcs(var_map: Dict[int, List[Dict[int, bool]]]
             ) -> Set[Tuple[int, int]]:
    arcs = set()

    for key, item in var_map.items():
        for key2, item2 in var_map.items():

            # if the neighbors have ANY in common, add those to the arcs
            if (
                not set(item[0].keys()).isdisjoint(item2[0].keys())
                and key != key2
            ):
                arcs.add((key, key2))

    return arcs


def revise(xi: int, xj: int, var_map: Dict[int, List[Dict[int, bool]]]
           ) -> bool:
    revised = False

    for x in list(var_map[xi]):
        result = [any([key in y and value != y[key]
                       for key, value in x.items()]) for y in var_map[xj]]

        if all(result):
            var_map[xi].remove(x)
            revised = True

    return revised


def propagate(var_map: Dict[int, List[Dict[int, bool]]],
              arcs: Set[Tuple[int, int]]) -> Dict[int, List[Dict[int, bool]]]:

    arcs_copy = arcs.copy()

    # while set is not empty
    while arcs:

        # get the first pair
        xi, xj = arcs.pop()

        if revise(xi, xj, var_map):

            if len(var_map[xi]) == 0:
                print(
                    "shouldn't get here, only using solvable CSP problems")

            # add to the queue all arcs (Xk,Xi) where Xk is a neighbor of Xi
            for arc in arcs_copy:
                if arc[1] == xi:
                    arcs.add(arc)

    return var_map


def sweep_mines(board: List[List[Optional[int]]]) -> Generator[int, int, None]:

    n_cols = len(board[0])

    while True:

        # get a var_map with reduced options
        var_map = get_vars(board)
        arcs = get_arcs(var_map)
        propagate(var_map, arcs)

        # determine safe index to query
        query = 0
        for variable in var_map.values():

            # combine all dicts into a single one with tuples of all the values
            combined = {}
            for k in variable[0].keys():
                combined[k] = tuple(combined[k] for combined in variable)

            # query becomes any index that has all falses
            for k, i in combined.items():
                if not any(i):
                    query = k
                    break

        clue = (yield query)

        # update board
        board[query // n_cols][query % n_cols] = clue
