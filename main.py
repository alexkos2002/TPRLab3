import math
import csv
import io

LOG_FILE_NAME = "logs.csv"

latin_months_nums = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

transport_price_per_unit = 10

clothes_to_weights = {
    "Блайзер": 0.5,
    "Бушлат": 4,
    "Ватні штани": 2,
    "В'єтнамки": 0.5,
    "Джинси": 1,
    "Кепка": 0.5,
    "Кросівки": 1,
    "Куртка": 2,
    "Пальто": 3,
    "Рукавички": 0.5,
    "Светр": 1,
    "Сорочка": 0.5,
    "Футболка": 0.5,
    "Черевики": 1.5,
    "Чоботи": 2,
    "Шапка": 1,
    "Шорти": 0.5,
    None: 0
}

clothes_to_prices = {
    "Блайзер": 6,
    "Бушлат": 16,
    "Ватні штани": 24,
    "В'єтнамки": 2,
    "Джинси": 12,
    "Кепка": 6,
    "Кросівки": 12,
    "Куртка": 24,
    "Пальто": 12,
    "Рукавички": 6,
    "Светр": 12,
    "Сорочка": 6,
    "Футболка": 6,
    "Черевики": 18,
    "Чоботи": 8,
    "Шапка": 4,
    "Шорти": 6,
    None: 0
}

clothes_sets_strategies = [
    ["Шапка", "Бушлат", "Рукавички", "Ватні штани", "Чоботи"],
    ["Шапка", "Пальто", "Рукавички", "Джинси", "Чоботи"],
    ["Кепка", "Куртка", None, "Джинси", "Черевики"],
    [None, "Светр", None, "Джинси", "Кросівки"],
    ["Блайзер", "Сорочка", None, "Джинси", "Кросівки"],
    ["Блайзер", "Футболка", None, "Шорти", "В'єтнамки"]
]

clothes_sets_temperature_ranges = [[-math.inf, -10], [-9, 0], [1, 10], [11, 20], [21, 30], [31, math.inf]]

return_in_months_probabilities = [1 / 12 for i in range(12)]

return_in_season_probabilities = [1 / 3 for i in range(3)]

return_rather_in_winter_probabilities = [0.1666, 0.1666, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.1666]

return_in_month_prorated_to_days_num_probabilities = [31 / 366, 29 / 366, 31 / 366, 30 / 366, 31/ 366, 30 / 366, 31 / 366, 31 / 366,
                                            30 / 366, 31 / 366, 30 / 366, 31 / 366]

months_av_temperatures = [-23, -19, -9, 3, 11, 17, 20, 18, 12, 2, -11, -21]

winter_months_av_temperatures = [-21, -23, -19]

spring_months_av_temperatures = [-9, 3, 11]

summer_months_av_temperatures = [17, 20, 18]

autumn_months_av_temperatures = [12, 2, -11]

def get_clothes_set_temperature_range_idx_for_temperature(temperature, clothes_sets_temperature_ranges):
    for temp_range_idx in range(len(clothes_sets_temperature_ranges)):
        if temperature >= clothes_sets_temperature_ranges[temp_range_idx][0] and \
                temperature <= clothes_sets_temperature_ranges[temp_range_idx][1]:
            return temp_range_idx
    return -1

def get_transportation_price_for_clothes_set(clothes_set, clothes_to_weights, transport_price_per_unit):
    return sum([clothes_to_weights[clothing] for clothing in clothes_set]) * transport_price_per_unit

def get_updated_clothes_prices_after_return(clothes_to_prices):
    return {clothing: clothes_to_prices[clothing] + 2 for clothing in clothes_to_prices}

def generate_csv_log_string(strategy_num, month_num, trans,  clothes_added_after_return, clothes_added_after_return_prices):
    log_string = "H" + str(strategy_num + 1)
    clothes_added_after_return_string = " | ".join([clothing for clothing in clothes_added_after_return])
    if (len(clothes_added_after_return_prices) == 0):
        clothes_added_after_return_prices_string = "0"
    else:
        clothes_added_after_return_prices_string = " + ".join(str(price) for price in clothes_added_after_return_prices)
        clothes_added_after_return_prices_string += " = " + str(sum(clothes_added_after_return_prices))
    log_string = log_string + "," + latin_months_nums[month_num] + "," + str(trans) + "," + clothes_added_after_return_string + " " + \
                 clothes_added_after_return_prices_string
    return log_string

def write_csv_log_strings_to_file(csv_logs, file_path):
    f = io.open(file_path, 'w', encoding='utf-16', newline ='')
    w = csv.writer(f)
    w.writerows([log.split(',') for log in csv_logs])
    f.close()


def find_utilities_of_clothes_set_strategies(clothes_to_weights, clothes_to_prices, clothes_sets_strategies,
                                             clothes_sets_temperature_ranges, return_in_time_range_probabilities,
                                             time_range_av_temperatures, update_clothes_prices_func):
    utilities_of_strategies = []
    csv_logs = []
    clothes_to_prices_after_return = update_clothes_prices_func(clothes_to_prices)
    clothes_added_after_return = []
    clothes_added_after_return_prices = []
    cur_strategy_utility = 0
    cur_strategy_for_time_range_utility = 0
    cur_clothes_set_strategy = None
    for clothes_set_strategy_idx in range(len(clothes_sets_strategies)):
        cur_clothes_set_strategy = clothes_sets_strategies[clothes_set_strategy_idx]
        for time_range_idx in range(len(return_in_time_range_probabilities)):
            cur_time_range_av_temperature = time_range_av_temperatures[time_range_idx]
            cur_clothes_set_temperature_range_idx = get_clothes_set_temperature_range_idx_for_temperature(cur_time_range_av_temperature,
                                                                                                          clothes_sets_temperature_ranges)
            cur_transportation_price_for_clothes_set = get_transportation_price_for_clothes_set(clothes_sets_strategies[clothes_set_strategy_idx],
                                                                                 clothes_to_weights, transport_price_per_unit)
            if cur_clothes_set_temperature_range_idx == clothes_set_strategy_idx:
                cur_strategy_for_time_range_utility = cur_transportation_price_for_clothes_set
            else:
                cur_strategy_for_time_range_utility += get_transportation_price_for_clothes_set(clothes_sets_strategies[clothes_set_strategy_idx],
                                                                                 clothes_to_weights, transport_price_per_unit)
                clothes_set_for_temp_after_return = clothes_sets_strategies[cur_clothes_set_temperature_range_idx]
                for clothes_idx in range(len(cur_clothes_set_strategy)):
                    clothing_before_return = cur_clothes_set_strategy[clothes_idx]
                    clothing_after_return = clothes_set_for_temp_after_return[clothes_idx]
                    if clothing_before_return != clothing_after_return:
                        if clothing_after_return != None:
                            clothing_added_after_return_price = clothes_to_prices_after_return[clothing_after_return]
                            cur_strategy_for_time_range_utility += clothing_added_after_return_price
                            clothes_added_after_return.append(clothing_after_return)
                            clothes_added_after_return_prices.append(clothing_added_after_return_price)
            cur_strategy_utility += cur_strategy_for_time_range_utility * return_in_time_range_probabilities[time_range_idx]
            cur_csv_log = generate_csv_log_string(clothes_set_strategy_idx, time_range_idx, cur_transportation_price_for_clothes_set,
                                                  clothes_added_after_return, clothes_added_after_return_prices)
            print(cur_csv_log)
            csv_logs.append(cur_csv_log)
            cur_strategy_for_time_range_utility = 0
            clothes_added_after_return.clear()
            clothes_added_after_return_prices.clear()
        utilities_of_strategies.append(-round(cur_strategy_utility, 3))
        cur_strategy_utility = 0

    write_csv_log_strings_to_file(csv_logs, LOG_FILE_NAME)

    return utilities_of_strategies


    print(return_in_time_range_probabilities)
    print(get_updated_clothes_prices_after_return(clothes_to_prices))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(find_utilities_of_clothes_set_strategies(clothes_to_weights, clothes_to_prices, clothes_sets_strategies,
                                                   clothes_sets_temperature_ranges, return_in_months_probabilities,
                                                   months_av_temperatures, get_updated_clothes_prices_after_return))
