import numpy as np
import math


# Returns strength of support/resistance points based on the amount of time between them
# Longer periods may indicate a more significant support/resistance trend ...
def interval_strength(critical_points) -> float:
    result = 0
    for i, point in enumerate(critical_points):
        if i != 0:
            interval_length = (point[0] - critical_points[i - 1][0])
            result += sigmoid_function(interval_length, sensitivity=1 / (30 ** 2), deg=2)
    return result / (len(critical_points) - 1)


# Takes any positive input and maps it to value in interval (0,1)
# Sensitivity and degree both control how rapidly the result changes with the input
def sigmoid_function(n, sensitivity=1.00, deg=1) -> float:
    return 2 / 3.14159 * math.atan(sensitivity * n ** deg)


# Gets the index of the highest or lowest value in a list over a given interval
def get_extrema_index(data, a, b, maximum=True) -> int:
    i = a
    extrema_index = None
    extrema = None
    while i <= b:
        if extrema_index is None:
            extrema_index = i
            extrema = data[i]
        elif maximum and extrema < data[i] or (not maximum and extrema > data[i]):
            extrema_index = i
            extrema = data[i]
        i += 1
    return extrema_index


# triangle_strength determines how well the stock follows a triangular trend using mean absolute errors.
# lower scores would indicate perhaps a more volatile stock and a more chaotic trend ...
def triangle_strength(data, critical_points, support=True) -> float:
    result = 0
    for i, point in enumerate(critical_points):
        if i == len(critical_points) - 1:
            continue
        peak = 0
        next_point = critical_points[i + 1]
        if support:
            peak = get_extrema_index \
                (data, point[0], next_point[0], maximum=True)
        else:
            peak = get_extrema_index \
                (data, point[0], next_point[0], maximum=False)

        j, k = point[0], next_point[0]
        slope1 = (data[peak] - point[1]) / (peak - point[0])
        slope2 = (next_point[1] - data[peak]) / (next_point[0] - peak)

        f1 = lambda x: point[1] + slope1 * (x - point[0])
        f2 = lambda x: data[peak] + slope2 * (x - peak)

        deviance = 0
        while j <= k:
            if j < peak:
                deviance += abs(data[j] / f1(j) - 1)
            else:
                deviance += abs(data[j] / f2(j) - 1)
            j += 1

        deviance /= (next_point[0] - point[0])
        result += deviance

    result /= len(critical_points) - 1

    return 1 - result


# Mathematical model for determining the strength of a stock based on different interpretations
def historic_strength(data, critical_points, support=True) -> (float,):
    average_age_bias = interval_strength(critical_points)
    triangle_bias = triangle_strength(data, critical_points, support=support) ** 2

    # n_point_bias gives an advantage to stocks which have more tested support/resistance points ...
    n_point_bias = (len(critical_points)) ** 0.6

    raw_strength = 1.6 * (
            average_age_bias * n_point_bias * triangle_bias)
    return (round(sigmoid_function(raw_strength, sensitivity=1, deg=2), 2), round(average_age_bias, 3),
            round(triangle_bias, 3), len(critical_points) - 1)


# Return the moving average for a given data set containing decimal values
def simple_moving_average(data, period=14) -> [float, ]:
    ma = []
    i = period
    init_avg = np.sum(data[0:i]) / period  # Period must be non-zero
    ma.append(init_avg)
    while i < len(data):
        i += 1
        # It's more efficient to calculate each MA according to the last, as it takes O(1) time over O(period) ...
        init_avg = (init_avg * period - data[i - 15] + data[i - 1]) / period
        ma.append(init_avg)

    for x, avg in enumerate(ma):  # Round after calculations to retain accuracy ...
        ma[x] = round(avg, 3)

    return ma


# Determines when a moving average crosses a specific price
def ma_cross_over(ma_data, target_price, ma_period):
    i = 1
    last_cross_over = 0
    while i < len(ma_data):
        if (target_price - ma_data[i]) * (target_price - ma_data[i - 1]) < 0:
            last_cross_over = i + ma_period - 1
        i += 1
    return last_cross_over


# Return average extreme price within support/resistance intervals
def aim_price(data, critical_points, support=True) -> float:
    aim = 0
    for i, point in enumerate(critical_points):
        if i == 0:  # Only evaluating n_points-1 intervals ...
            continue
        if support:
            aim += max(data[critical_points[i - 1][0]: critical_points[i][0]])
        else:
            aim += min(data[critical_points[i - 1][0]: critical_points[i][0]])
    return aim / (len(critical_points) - 1)


# Decides if trend is support or resistance then returns all support/resistance points
def support_resistance_points(data, trend_duration_floor=12, trend_duration_ceil=18, trend_strength=0.90,
                              buffer=2.0) -> ([(int, float)], bool):
    points = []
    current_price = data[-1]

    support = None
    print("Ran")
    average_period = 14

    crossover = ma_cross_over(simple_moving_average(data, period=average_period), current_price, average_period)
    i = max(trend_duration_ceil, crossover)  # Only consider data in the relevant market period ...

    while i < len(data) - trend_duration_ceil:

        # Price is in range of current price, may be an ideal point ...
        if abs(data[i] - current_price) <= 0.01 * buffer * current_price:
            """Testing several t-values is beneficial as some local support/resistance points may not be clear over
            one specific slice of the data ...
            Range is reversed as it is optimal to look for a broader extrema point then a more local one ... """
            for t in reversed(range(trend_duration_floor, trend_duration_ceil + 1)):
                price_increment = data[i] * trend_strength * t * 0.01

                # Support
                if data[i - t] > data[i] + price_increment and \
                        data[i + t] > data[i] + price_increment:

                    if support is None or support:
                        support = True
                        points.append((i, data[i]))
                    else:
                        return [], False
                    i += t
                    break

                # Resistance
                elif data[i - t] < data[i] - price_increment and \
                        data[i + t] < data[i] - price_increment:
                    if support is None or not support:
                        support = False
                        points.append((i, data[i]))
                    else:
                        return [], False
                    i += t
                    break
        i += 1

    points.append((len(data) - 1, data[-1]))
    if support:
        return points, True
    return points, False
