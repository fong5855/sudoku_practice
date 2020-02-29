import numpy as np
import time
import cv2
import threading
from configparser import ConfigParser


class Sudoku:
    def __init__(self):
        self.data = np.zeros((9,9), dtype=np.int)
        self.row = []
        self.col = []
        self.blk = []
        self.n = np.arange(1, 10)
        self.init_by_data(self.data)

    def init_by_data(self, data: np.ndarray):
        self.data = data.copy()
        self.row.clear()
        self.col.clear()
        self.blk.clear()

        for i in range(9):
            self.row.append(np.unique(self.data[i,:]).tolist())
            self.col.append(np.unique(self.data[:,i]).tolist())
            self.blk.append(np.unique(self.data[int(3*int(i/3)):int(3*int(i/3+1)), int(3*(i%3)):int(3*int(i%3+1))]).tolist())

    def update_conditions(self):
        for i in range(9):
            self.row[i] = (np.unique(self.data[i,:]).tolist())
            self.col[i] = (np.unique(self.data[:,i]).tolist())
            self.blk[i] = (np.unique(self.data[int(3*int(i/3)):int(3*int(i/3+1)), int(3*(i%3)):int(3*int(i%3+1))]).tolist())

    def check(self, print_flag=True):
        self.update_conditions()
        check_flag = True
        for r in self.row:
            if np.setdiff1d(self.n, r).size != 0:
                check_flag = False
        for r in self.col:
            if np.setdiff1d(self.n, r).size != 0:
                check_flag = False
        for r in self.blk:
            if np.setdiff1d(self.n, r).size != 0:
                check_flag = False

        if print_flag:
            if check_flag:
                print("Sudoku constraint check = ", check_flag)
            else:
                print("row", self.row)
                print("column", self.col)
                print("block", self.blk)

        return check_flag


class SudokuSolver(Sudoku):
    def __init__(self):
        Sudoku.__init__(self)
        self.n = np.arange(1, 10)

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

        a = np.setdiff1d(self.n, self.col[j])
        b = np.setdiff1d(self.n, self.row[i])
        c = np.setdiff1d(self.n, self.blk[blk_index])
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


class SudokuGenerator(SudokuSolver):
    def __init__(self):
        SudokuSolver.__init__(self)
        self.n = np.arange(1, 10)
        self.gen_data = np.zeros((9, 9), dtype=np.int)
        self.step_2_success = False
        self.stop_gen = False

    def gen_blk(self, i_min, i_max, j_min, j_max):
        regen = True
        blk_index = int(j_min/3 + 3*int(i_min/3))
        while regen:
            for i in range(i_min, i_max):
                for j in range(j_min, j_max):
                    a = np.setdiff1d(self.n, self.col[j])
                    b = np.setdiff1d(self.n, self.row[i])
                    c = np.setdiff1d(self.n, self.blk[blk_index])
                    r = np.intersect1d(np.intersect1d(a, b), c)
                    self.update_conditions()

                    try:
                        self.data[i, j] = np.random.choice(r, 1)
                    except ValueError:
                        pass

            self.update_conditions()
            if np.intersect1d(self.n, self.blk[blk_index]).size is 9 or self.stop_gen:
                regen = False
            # else:
            #     print(np.intersect1d(self.n, self.blk[blk_index]))

    def timer(self):
        t = 0
        while True:
            time.sleep(0.5)
            if self.step_2_success:
                return
            elif t > 10:
                break
            t += 1
        self.stop_gen = True

    def gen(self, mask_rate=0.77):
        self.data = np.zeros((9,9), dtype=int)
        self.stop_gen = False

        print("stage 1..")
        self.data[0:3, 0:3] = np.random.choice(self.n, size=9, replace=False).reshape(3, -1)
        self.data[3:6, 3:6] = np.random.choice(self.n, size=9, replace=False).reshape(3, -1)
        self.data[6:9, 6:9] = np.random.choice(self.n, size=9, replace=False).reshape(3, -1)

        print("stage 2..")
        t = threading.Thread(target=SudokuGenerator.timer, args=[self])
        t.start()
        # self.gen_blk(0, 3, 3, 6)
        self.gen_blk(3, 6, 0, 3)
        # self.gen_blk(6, 9, 0, 3)
        # self.gen_blk(0, 3, 6, 9)

        self.step_2_success = True
        t.join()
        if self.stop_gen:
            return False

        print("stage 3..")
        self.init_by_data(self.data)
        self.solve(print_debug_info=False)
        if not self.check(print_flag=False):
            return False

        print(self.data)

        print("stage 4..")
        mm = self.data.copy()
        mm[np.random.choice([True, False], size=mm.shape, p=[mask_rate, 1 - mask_rate])] = 0
        print(mm)
        self.gen_data = mm.copy()

        self.solve(print_debug_info=False)
        print(self.data)
        return self.check(print_flag=True)


def test_gen(mask_rate):
    sg = SudokuGenerator()

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

    # sg.init_by_data(test_data)
    while not sg.gen(mask_rate):
        sg.init_by_data(test_data)
        print("generate question fail... regenerate again")

    img = draw(sg.gen_data)
    ans = draw(sg.data)
    cv2.imwrite("sudoku.png", img)
    cv2.imwrite("sudoku_ans.png", ans)


def draw(data, show_flag=False):
    blank_size = 50
    img_size = blank_size * 9
    img = np.zeros((img_size, img_size, 3), np.uint8) + 255
    for i in range(10):
        line_distance = int(img_size / 9) * i
        line_thickness = 1
        if i % 3 == 0:
            line_thickness = 5
        cv2.line(img, (0, line_distance), (img_size, line_distance), (255, 0, 0), line_thickness)
        cv2.line(img, (line_distance, 0), (line_distance, img_size), (255, 0, 0), line_thickness)

    w, h = data.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(w):
        for j in range(h):
            y = int(blank_size*i + blank_size/2 + 12)
            x = int(blank_size*j + blank_size/2 - 10)
            if data[i, j] <= 0:
                continue
            content = str(data[i,j])
            cv2.putText(img, content, (x, y), font, 1.2, (0, 0, 0), 2, cv2.LINE_AA)

    if show_flag:
        cv2.imshow("test", img)
        cv2.waitKey()

    return img


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    mask_rate_ = float(config.get("main", "mask_rate"))

    test_gen(mask_rate_)
    # draw()
