import pandas as pd
import numpy as np
import gurobipy as grb
import math
import time
import time

np.random.seed(0)

'''
alpha_list: np.arrar
'''
# 根据需求函数返回demand和二分法上下界
def generate_one_demand_uniform(N):
    # 生成1-5之间的均匀分布
    return np.random.randint(1, 6, size=(N, 1))

def generate_initial_bound_uniform(alpha_list):
    # upper_bound为service_level作为分位点
    return 0, sum([4 * alpha for alpha in alpha_list])

# 计算当前capacity在原文G rule下的dist(命名为gap)
def calculate_temp_gap(alpha_list, Q, print_info, T):
    '''
    T: 要迭代的次数
        算法1中为4N/gap^2
        算法2中为[1,4N/gap^2]的均匀分布
    '''
    N = len(alpha_list)
    r_array = np.copy(alpha_list) # 初始化r(0)
    for _ in range(T):
        A = generate_one_demand_uniform(N)
        A = A.reshape(1, -1) # 转换为二维数组
        solution, _ = solve_binaryIP(r_array, A, [Q]) # 只关心最优解
        if solution is not None:
            r_array = [r_array[i] + alpha_list[i] - solution[i] for i in range(N)] # 更新r_array
        elif print_info:
            print("function calculate_temp_gap debug")
    temp_gap = math.sqrt(sum([(r/T)**2 for r in r_array if r > 0])) # 计算temp_gap
    if print_info:
        print(temp_gap)
    return temp_gap, solution

def solve_binaryIP(c, A, b):
    # 调用gurobi求解IP，返回最优解和目标值
    # start_time = time.time()
    model = grb.Model()
    model.setParam('OutputFlag', 0) # 不输出求解过程
    x = model.addVars(len(c), vtype=grb.GRB.BINARY)
    expr = grb.quicksum(c[i]*x[i] for i in range(len(c)))
    model.setObjective(expr, grb.GRB.MAXIMIZE)
    num_constraints = len(b)
    for i in range(num_constraints):
        constraint = grb.LinExpr()
        constraint += sum(A[i][j] * x[j] for j in range(len(x)))
        model.addConstr(constraint <= b[i], f"c{i}")
    model.optimize()
    # end_time = time.time()
    if model.status == grb.GRB.OPTIMAL:
        solution = [x[i].x for i in range(len(c))]
        # solve_time = end_time - start_time
        # print("Solution time:", solve_time, "seconds")
        # print("Optimal Solution:", model.ObjVal)
        return solution, model.ObjVal
    else:
        return None

# 算法主程序
def algorithm_one(alpha_list, max_gap, max_iteration=float('inf'), print_info = False):
    '''
    N: # of custermers
    alpha_list: service level of each customer
    max_gap: tolerence distance of unmet service level
    '''
    N = len(alpha_list)
    T = math.ceil(4 * N / max_gap**2) + 1 # 模拟次数
    lower, upper = generate_initial_bound_uniform(alpha_list)
    init_upper = upper
    if print_info:
        print('Upper_bound: ',upper)
    temp_gap = max_gap + 1
    temp_iteration = 0
    # 二分搜索
    while lower < upper:
        temp_Q = (lower + upper) // 2
        start_time = time.time()
        temp_gap, _ = calculate_temp_gap(alpha_list, temp_Q, print_info, T)
        end_time = time.time()
        if print_info:
            print(f"二分法第{temp_iteration+1}次循环时间：{end_time - start_time}")
            print("temp_Q:", temp_Q)
        if temp_gap < max_gap: # 当前capacity满足条件
            upper = temp_Q
        else:
            lower = temp_Q + 1
        temp_iteration += 1
    if lower >= math.floor(init_upper):
        print("找不到满足条件的Q")
    return lower


def algorithm_two(alpha_list, Q, max_gap, max_iteration=float('inf'), print_info = False):
    '''
    Q: capacity
    '''
    N = len(alpha_list)
    random_t = np.random.randint(1, 4 * N / max_gap**2)
    return calculate_temp_gap(alpha_list, Q, print_info, random_t)


# 测试solve_binaryIP
def test_knapsack_problem(test_num=100):
    def knapsack_problem(weights, values, capacity):
        n = len(weights)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for j in range(1, capacity + 1):
                if weights[i - 1] <= j:
                    dp[i][j] = max(values[i - 1] + dp[i - 1][j - weights[i - 1]], dp[i - 1][j])
                else:
                    dp[i][j] = dp[i - 1][j]

        return dp[n][capacity]

    # Generate 100 test cases
    test_cases = []
    for _ in range(test_num):
        # Generate random weights, values, and capacity
        weights = np.random.randint(1, 10, size=10)
        values = np.random.randint(1, 10, size=10)
        capacity = np.random.randint(10, 20)
        test_cases.append((weights, values, capacity))

    # Compare solutions and running time for each test case
    dp_total_time = 0
    ip_total_time = 0

    for weights, values, capacity in test_cases:
        start_time = time.time()
        dp_solution = knapsack_problem(weights, values, capacity)
        end_time = time.time()
        dp_total_time += end_time - start_time

        start_time = time.time()
        _, ip_solution = solve_binaryIP(values, [weights], [capacity])
        end_time = time.time()
        ip_total_time += end_time - start_time

        if dp_solution == ip_solution:
            print("Solutions are the same")
        else:
            print("Solutions are different")

    print("DP Total Time:", dp_total_time, "seconds")
    print("IP Total Time:", ip_total_time, "seconds")
    # 发现IP的求解速度会更慢


    
# 测试
## 测试函数
def test_algorithm_one(N, max_gap, max_iteration):
    alpha_list = np.random.rand(N)
    Q = algorithm_one(alpha_list, max_gap, max_iteration, print_info=True)
    return Q

def test_algorithm_two(N, max_gap, max_iteration):
    alpha_list = np.random.rand(N)
    Q = generate_initial_bound_uniform(alpha_list)[1]*np.random.rand()
    print(Q)
    return algorithm_two(alpha_list, Q, max_gap, max_iteration, print_info=True)


## 测试实例
# print(test_algorithm_one(10, 0.1, 100))
# test_knapsack_problem()
print(test_algorithm_two(10, 0.1, 100))