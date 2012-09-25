import sys
import copy
import heapq


class Board(object):

    def __init__(self, blocks):
        self.blocks = blocks
        self.cache = {}

    def dimension(self):
        return len(self.blocks)

    def hamming(self):
        dim = self.dimension()
        dist = 0
        for i in range(dim):
            for j in range(dim):
                n = i * dim + j + 1
                if self.blocks[i][j] not in (0, n):
                    dist += 1
        return dist

    def manhattan(self):
        key = str(self)
        if key not in self.cache:
            dim = self.dimension()
            dist = 0
            for i in range(dim):
                for j in range(dim):
                    n = self.blocks[i][j]
                    if n != 0:
                        n -= 1
                        row = n / dim
                        col = n % dim
                        dist += abs(row-i) + abs(col-j)
            self.cache[key] = dist
        
        return self.cache[key]

    distance = manhattan

    def is_goal(self):
        return self.distance() == 0

    def _swap(self, p1, p2):
        blocks = copy.deepcopy(self.blocks)
        tmp = blocks[p1[0]][p1[1]]
        blocks[p1[0]][p1[1]] = blocks[p2[0]][p2[1]]
        blocks[p2[0]][p2[1]] = tmp
        return Board(blocks)

    def neighbors(self):
        dim = self.dimension()

        blank = None
        for i in range(dim):
            if blank:
                break
            for j in range(dim):
                if self.blocks[i][j] == 0:
                    blank = (i, j)
                    break

        def _iter():
            row, col = blank
            if row > 0:
                yield self._swap(blank, (row-1, col))
            if row < dim-1:
                yield self._swap(blank, (row+1, col))
            if col > 0:
                yield self._swap(blank, (row, col-1))
            if col < dim-1:
                yield self._swap(blank, (row, col+1))

        return _iter()

    def __str__(self):
        dim = self.dimension()
        arr = [str(dim)]
        arr.extend([' '.join([('%2d'%n) for n in row]) \
            for row in self.blocks])
        return '\n'.join(arr)

    @staticmethod
    def load(fp=sys.stdin):
        N = int(fp.readline())

        blocks = [ map(int, fp.readline().split()) \
            for i in range(N) ]
        assert N == len(blocks) ==len(blocks[0])

        return Board(blocks)

    def __eq__(self, that):
        return str(self) == str(that)

    def __ne__(self, that):
        return not self == that

    def __hash__(self):
        return hash(str(self))

    def twin(self):
        dim = self.dimension()
        assert dim > 1
        if self.blocks[0][0] != 0 and self.blocks[0][1] != 0:
            return self._swap((0, 0), (0, 1))
        return self._swap((1, 0), (1, 1))


class Solver(object):

    class Engine(object):

        def __init__(self, initial):
            self.queue = PQ()
            self.queue.push(initial.distance(), (initial, 0, None))
            self.sols = {initial: None}
            self.see = set()

        def step(self):
            queue = self.queue
            assert not queue.empty()

            #search node, moves so far, previous search node
            node, moves, prev = queue.pop()
            self.sols[node] = prev

            if node.is_goal():
                return moves, self.sols, node

            self.see.add(node)
            moves += 1
            for neighbor in node.neighbors():
                if neighbor != prev and neighbor not in self.see:
                    priority = neighbor.distance() + moves
                    queue.push(priority, (neighbor, moves, node))

    def __init__(self, initial):
        self._moves, self._solutions = self._solve(initial)
    
    def _solve(self, initial):
        engine1 = self.Engine(initial)
        twin = initial.twin()
        engine2 = self.Engine(twin)

        while 1:
            ret1 = engine1.step()
            if ret1:
                moves, sols, end = ret1
                path = []
                while end:
                    path.insert(0, end)
                    end = sols[end]
                return moves, path

            ret2 = engine2.step()
            if ret2:
                return -1, []


    def is_solvable(self):
        return self.moves > -1

    @property
    def moves(self):
        return self._moves

    @property
    def solution(self):
        return self._solutions

    
class PQ(object):

    def __init__(self):
        self.heap = []

    def push(self, priority, item):
        heapq.heappush(self.heap, (priority, item))

    def pop(self):
        assert not self.empty()
        return heapq.heappop(self.heap)[1]

    def empty(self):
        return not self.heap
        

def main():
    initial = Board.load()

    solver = Solver(initial)
    if not solver.is_solvable():
        print 'no solution possible'
    else:
        print 'minimum nuber of moves =', solver.moves
        for board in solver.solution:
            print board
            print


def test():
    from StringIO import StringIO
    case1 = StringIO('''3
 1  2  3
 4  6  5
 7  0  8
''')

    case2 = StringIO('''3
 1  2  3
 4  6  0
 7  8  5
''')

    case3 = StringIO('''3
 0  2  3
 4  1  6
 7  8  5
''')

    board = Board.load(case3)
    print board
    print 

    for neighbor in board.neighbors():
        print neighbor

def test2():
     from StringIO import StringIO
     case1 = StringIO('''3
 8  1  3
 4  0  2
 7  6  5
''')
     print Board.load(case1).manhattan()



if __name__ == '__main__':
    #test2()
    main()
