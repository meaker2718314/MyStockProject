import yfinance as yf
import index as index
import analysis as analysis
from datetime import date
import matplotlib.pyplot as plt
import numpy as np


def order_by_strength(stock_picks):
    stock_picks.sort(key=lambda z: z[2][0])
    stock_picks.reverse()
    return stock_picks


def order_by_gain(stock_picks):
    stock_picks.sort(key=lambda z: z[1])
    stock_picks.reverse()
    return stock_picks


def order_by_triangle_strength(stock_picks):
    stock_picks.sort(key=lambda z: z[2][2])
    stock_picks.reverse()
    return stock_picks


def retrieve_analysis(ticker_list) -> [(str, float, float)]:
    stock_picks = []
    for ticker in ticker_list:
        if not isinstance(ticker, str):  #
            continue

        stock = yf.Ticker(ticker)
        historic_data = stock.history(period='1y')
        price_list = list(historic_data['Close'])

        if not price_list:  # Symbol de-listed or another problem with getting stock prices ...
            continue

        for i, price in enumerate(price_list):  # Easier to handle and visualize with limited decimal accuracy ...
            price_list[i] = round(price, 3)
        price_action_info = \
            analysis.support_resistance_points(price_list, buffer=2.80)

        if len(price_action_info[0]) >= 2:
            if price_action_info[1]:
                target = analysis.aim_price(price_list, price_action_info[0], support=True)
                strength = analysis.historic_strength(price_list, price_action_info[0], support=True)
            else:
                target = analysis.aim_price(price_list, price_action_info[0], support=False)
                strength = analysis.historic_strength(price_list, price_action_info[0], support=False)

            gain_potential = abs(target / price_list[-1] - 1)  # 0.24 would mean 24% gain potential, etc.
            trend_type = "Support" if price_action_info[1] else "Resistance"
            stock_picks.append((ticker, round(gain_potential, 3),
                                strength, round(price_list[-1], 3), round(target, 3),
                                price_action_info[0], price_list, trend_type))
    return stock_picks


if __name__ == '__main__':
    # Change inner method to change selected index, change qty of stocks analyzed by changing sublist length ...
    # *** PLEASE NOTE *** Algorithm can take several minutes to terminate when analyzing very large quantities of data

    tickers = index.russell_1000()
    results = retrieve_analysis(tickers)
    print(results)
    results = order_by_strength(results)  # Sort results by their overall strength

    # Open text file to write results to
    f = open("stock_info.txt", "a")
    f.truncate(0)  # Clear text file

    f.write(f'Date: {date.today()}\n\n')
    f.write('*** Note that the parameters provided in the strength category are defined as the following: ***\n')
    f.write("(Overall Strength, Interval Length Strength, Triangle Strength, # Resistance/Support Points)\n")
    f.write("The specific properties of these indicators can be found in the code documentation\n\n")

    results = filter(lambda item: item[2][0] >= 0.45 and item[1] >= 0.25, results)  # Remove poor results from list

    f.write(f'STOCK   GAIN    {"STRENGTH":<28}CURRENT   TARGET   TYPE \n\n')
    for result in results:
        f.write(f'{result[0]:<8}{str(result[1]):<8}'
                f'{str(result[2]):<28}${str(result[3]):<9}${str(result[4]):<8}{result[7]}\n')

        plt.clf()  # Clear the current matplotlib plot, prevents unwanted overlay ...

        if result[3] < result[4]:
            lower_limit = 0.7 * result[3]
            upper_limit = 1.3 * result[4]
        else:
            lower_limit = 0.70 * result[4]
            upper_limit = 1.3 * result[3]

        plt.ylim(lower_limit, upper_limit)  # Condense price range shown by the plot ...

        action_points = result[5]
        price_data = result[6]
        trend = result[7]

        # Draw lines / trend approximations

        plt.plot()
        plt.plot([i for i in range(len(result[6]))], result[6], color="black")

        for i, point in enumerate(action_points):
            if i == 0:
                continue
            extrema = analysis.get_extrema_index(
                price_data, action_points[i - 1][0], point[0], maximum=trend == "Support")
            plt.plot([action_points[i - 1][0], extrema], [action_points[i - 1][1], price_data[extrema]],
                     color='r', linestyle='--', lw=2)

            plt.plot([extrema, point[0]], [price_data[extrema], point[1]], color='r', linestyle='--', lw=2)

        x = np.linspace(0, len(price_data))

        plt.plot(x, 0*x+result[3], color='b', linestyle='-', lw=1)
        plt.plot(x, 0*x+result[4], color='g', linestyle='-', lw=1, label='Target Price')
        plt.xlabel("Time (Days)")
        plt.ylabel("Stock Price (USD)")
        plt.title(f"{result[0]} - {date.today()}")
        plt.legend(loc='best')
        plt.savefig(f"stock_images/{result[0]}.png")

    f.close()
