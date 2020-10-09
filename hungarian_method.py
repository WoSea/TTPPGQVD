import sys
from typing import NewType, Sequence, Tuple
Matrix = NewType('Matrix', Sequence[Sequence[int]])

class Hungarian:
    
    def __init__(self):
        self.mat = None
        self.row_covered = []
        self.col_covered = []
        self.starred = None
        self.n = 0
        self.Z0_r = 0
        self.Z0_c = 0
        self.series = None
    
    def solve(self, cost_matrix: Matrix):
        self.mat = cost_matrix
        self.n = len(self.mat)
        self.row_covered = [False for i in range(self.n)]
        self.col_covered = [False for i in range(self.n)]
        self.Z0_r = 0
        self.Z0_c = 0
        self.series = [[0 for j in range(2)] for j in range(self.n*2)]
        self.starred = [[0 for j in range(self.n)] for j in range(self.n)]

        done = False
        step = 1

        steps = { 1 : self.step1,
                  2 : self.step2,
                  3 : self.step3,
                  4 : self.step4,
                  5 : self.step5,
                  6 : self.step6
                  }

        while not done:
            try:
                func = steps[step]
                step = func()
            except:
                done = True
                
        results = []
        for i in range(self.n):
            for j in range(self.n):
                if self.starred[i][j] == 1:
                    results += [(i, j)]

        return results

    def step1(self):
        """
        Ở mỗi hàng, tìm phần tử nhỏ nhất và lấy các phần tử còn lại trừ cho nó
        và trừ cho chính nó. Bước sang bước 2
        """
        n = self.n
        for i in range(n):
            vals = [x for x in self.mat[i]]
            minval = min(vals)
            for j in range(n):
                self.mat[i][j] -= minval
        return 2

    def step2(self):
        """
        Tìm một số 0 (Z) trong ma trận. Nếu không có starred 0 nào trong hàng/ cột 
        ,ta sẽ star Z. Lặp lại cho mỗi phần tử trong ma trận.
        Đi tới bước 3
        """
        for i in range(self.n):
            for j in range(self.n):
                if (self.mat[i][j] == 0) and \
                        (not self.col_covered[j]) and \
                        (not self.row_covered[i]):
                    self.starred[i][j] = 1
                    self.col_covered[j] = True
                    self.row_covered[i] = True
                    break

        self.__clear_covers()
        return 3

    def step3(self): 
        n = self.n
        count = 0
        for i in range(n):
            for j in range(n):
                if self.starred[i][j] == 1 and not self.col_covered[j]:
                    self.col_covered[j] = True
                    count += 1

        if count >= n:
            step = 7 # done
        else:
            step = 4

        return step

    def step4(self): 
        step = 0
        done = False
        row = 0
        col = 0
        star_col = -1
        while not done:
            (row, col) = self.__find_a_zero(row, col)
            if row < 0:
                done = True
                step = 6
            else:
                self.starred[row][col] = 2
                star_col = self.__find_star_in_row(row)
                if star_col >= 0:
                    col = star_col
                    self.row_covered[row] = True
                    self.col_covered[col] = False
                else:
                    done = True
                    self.Z0_r = row
                    self.Z0_c = col
                    step = 5

        return step

    def step5(self): 
        count = 0
        series = self.series
        series[count][0] = self.Z0_r
        series[count][1] = self.Z0_c
        done = False
        while not done:
            row = self.__find_star_in_col(series[count][1])
            if row >= 0:
                count += 1
                series[count][0] = row
                series[count][1] = series[count-1][1]
            else:
                done = True

            if not done:
                col = self.__find_prime_in_row(series[count][0])
                count += 1
                series[count][0] = series[count-1][0]
                series[count][1] = col

        self.__convert_series(series, count)
        self.__clear_covers()
        self.__erase_primes()
        return 3

    def step6(self): 
        minval = self.__find_smallest()
        for i in range(self.n):
            for j in range(self.n):
                if self.row_covered[i]:
                    self.mat[i][j] += minval
                if not self.col_covered[j]:
                    self.mat[i][j] -= minval
        return 4

    def __find_smallest(self):
        """Tìm giá trị nhỏ nhất chưa bị phủ trong ma trận."""
        minval = sys.maxsize
        for i in range(self.n):
            for j in range(self.n):
                if (not self.row_covered[i]) and (not self.col_covered[j]):
                    if minval > self.mat[i][j]:
                        minval = self.mat[i][j]
        return minval

    def __find_a_zero(self, i0: int = 0, j0: int = 0):
        """Tìm giá trị đầu tiên không bị phủ là 0"""
        row = -1
        col = -1
        i = i0
        n = self.n
        done = False

        while not done:
            j = j0
            while True:
                if (self.mat[i][j] == 0) and \
                        (not self.row_covered[i]) and \
                        (not self.col_covered[j]):
                    row = i
                    col = j
                    done = True
                j = (j + 1) % n
                if j == j0:
                    break
            i = (i + 1) % n
            if i == i0:
                done = True

        return (row, col)

    def __find_star_in_row(self, row: Sequence[int]): 
        col = -1
        for j in range(self.n):
            if self.starred[row][j] == 1:
                col = j
                break

        return col

    def __find_star_in_col(self, col: Sequence[int]): 
        row = -1
        for i in range(self.n):
            if self.starred[i][col] == 1:
                row = i
                break

        return row

    def __find_prime_in_row(self, row): 
        col = -1
        for j in range(self.n):
            if self.starred[row][j] == 2:
                col = j
                break

        return col


    def __convert_series(self,
                       series: Matrix,
                       count: int): 
        for i in range(count+1):
            if self.starred[series[i][0]][series[i][1]] == 1:
                self.starred[series[i][0]][series[i][1]] = 0
            else:
                self.starred[series[i][0]][series[i][1]] = 1


    def __clear_covers(self):
        for i in range(self.n):
            self.row_covered[i] = False
            self.col_covered[i] = False


    def __erase_primes(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.starred[i][j] == 2:
                    self.starred[i][j] = 0
