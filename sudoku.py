import numpy as np
import time


class Sudoku:
    def __init__(self):
        self.data = np.zeros((9,9), dtype=np.int)
        self.row = []
        self.col = []
        self.blk = []

    def init_by_data(self, data: np.ndarray):
        self.data = data.copy()
        self.row = []
        self.col = []
        self.blk = []

        for i in range(9):
            self.row.append(np.unique(self.data[i,:]).tolist())
            self.col.append(np.unique(self.data[:,i]).tolist())
            self.blk.append(np.unique(self.data[int(3*int(i/3)):int(3*int(i/3+1)), int(3*(i%3)):int(3*int(i%3+1))]).tolist())
        print(self.row)
        print(self.col)
        print(self.blk)

    def update_conditions(self):
        for i in range(9):
            self.row[i] = (np.unique(self.data[i,:]).tolist())
            self.col[i] = (np.unique(self.data[:,i]).tolist())
            self.blk[i] = (np.unique(self.data[int(3*int(i/3)):int(3*int(i/3+1)), int(3*(i%3)):int(3*int(i%3+1))]).tolist())


class SudokuSolver(Sudoku):
    def __init__(self):
        self.__init_subclass__()

    def guess(self, i, j):
        num = self.data[i, j]
        # remove element
        if num in self.col[j]:
            self.col[j].remove(num)
        if num in self.row[i]:
            self.row[i].remove(num)
        # if num in self.blk[int(i/3 + 3*int(j/3))]:
        blk_index = int(j/3 + 3*int(i/3))
        if num in self.blk[blk_index]:
            self.blk[blk_index].remove(num)

        n = np.arange(1, 10)
        a = np.setdiff1d(n, self.col[j])
        b = np.setdiff1d(n, self.row[i])
        c = np.setdiff1d(n, self.blk[blk_index])
        r = np.intersect1d(np.intersect1d(a, b), c)
        # print(i, j, r)

        result = False
        for rr in r:
            if rr > num:
                self.data[i, j] = rr
                result = True
                break

        # clear guess number
        if result is False:
            self.data[i, j] = 0
        self.update_conditions()
        return result

    def clear_guess(self, i, j):
        self.data[i, j] = 0
        self.update_conditions()

    def solve(self, print_debug_info=False):
        position = 0
        known = (self.data > 0).copy()
        counter = 0
        while True:
            # skip the known value
            while position < 81 and known[int(position/9), int(position%9)]:
                position += 1
            if position >= 81:
                break

            result = self.guess(int(position/9), int(position%9))
            if print_debug_info and counter % 5000 == 0:
                print(counter)
                print(self.data)
            counter += 1

            if result is False:
                position -= 1
                while position >= 0 and known[int(position/9), int(position%9)]:
                    position -= 1
                if position < 0:
                    break
            else:
                position += 1


def test():
    ss = SudokuSolver()

    print("simple question test")
    test_data = np.asarray([
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],

        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],

        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])
    ss.init_by_data(test_data)
    t_start = time.time()
    ss.solve()
    t_end = time.time()
    print("using time = ", t_end - t_start)
    print(ss.data)
    # input("input any word to continue")

    print("simple question in WiKi")
    test_data = np.asarray([
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],

        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],

        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ])
    ss.init_by_data(test_data)

    t_start = time.time()
    ss.solve()
    t_end = time.time()
    print("using time = ", t_end - t_start)
    print(ss.data)

    print("random question")
    test_data = np.asarray([
        [0, 7, 0, 0, 0, 2, 0, 0, 0],
        [9, 0, 0, 0, 6, 0, 3, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 8, 0],

        [0, 0, 8, 0, 3, 0, 0, 0, 1],
        [0, 9, 0, 7, 0, 4, 0, 6, 0],
        [3, 0, 0, 0, 5, 0, 9, 0, 0],

        [0, 1, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 6, 0, 1, 0, 0, 0, 5],
        [0, 0, 0, 4, 0, 0, 0, 3, 0],
    ])
    ss.init_by_data(test_data)

    t_start = time.time()
    ss.solve()
    t_end = time.time()
    print("using time = ", t_end - t_start)
    print(ss.data)

    print("The hardest question in this world")
    test_data = np.asarray([
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],

        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],

        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0],
    ])

    ss.init_by_data(test_data)
    t_start = time.time()
    ss.solve()
    t_end = time.time()
    print("using time = ", t_end - t_start)
    print(ss.data)


if __name__ == '__main__':
    test()
