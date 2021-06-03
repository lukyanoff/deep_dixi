import random
from multiprocessing import Pool
import tensorflow as tf

from tqdm import tqdm
from src.data_gen.dataset_generator import generate_sliced_data_set_v1, generate_sliced_data_set_v2
from src.iterator import batch, flatten
from src.model.StockModel import StockModel
from src.calulation.utils import get_all_stocks
import pickle
import numpy as np

min_value = 1 / 100
def parse_loaded_data(i, x_keys, y_key):
    x = [i.get(key) for key in x_keys]
    y =  [1] if i[y_key] > min_value else [0]
    return x, y

def balance_array(arr):
    pos = list(filter(lambda a:a[1][0]==1, arr))

    pos_len = len(pos)
    if (pos_len==0):
        return arr

    delta = len(arr)-pos_len
    cho = [random.choice(pos) for _ in range(delta)]
    print("Add ", len(arr), pos_len, delta)

    result = []
    result.extend(arr)
    result.extend(cho)

    random.shuffle(result)
    return result

def save_to_file(stock):
    try:
        folder = "c:/_data_for_training"
        file_name = f"{folder}/{stock.symbol}.dataset"
        def _gen():
            data = generate_sliced_data_set_v1(stock)
            example = next(data)
            keys = set(example.keys())
            raw = {"date", "close", "open", "date", "high", "low", "volume", "profit", "loss"}
            x_keys = list(keys - raw)
            x_keys.sort()
            result = map(lambda a: parse_loaded_data(a, x_keys, 'profit'), data)

            batched_result = batch(result, 5000)
            batched_result_balanced = map(balance_array, batched_result)
            batched_result_flatten = flatten(batched_result_balanced)
            return batched_result_flatten

        dataset = tf.data.Dataset.from_generator(_gen,  output_signature=(
                  tf.TensorSpec(shape=(43, 60), dtype=tf.float32),
                  tf.TensorSpec(shape=(1,), dtype=tf.int8)))
        print("Saving ds", file_name)
        tf.data.experimental.save(dataset, file_name)
        print("Saved", file_name)
        return None, "OK"
    except Exception as e:
        print(e)
        raise
        return e, None

def main():
    symbols = [
        StockModel.parse("NASDAQ:MSFT"),
        StockModel.parse("NASDAQ:AAPL"),
        StockModel.parse("NASDAQ:TEAM"),
        StockModel.parse("NASDAQ:TSLA"),
        StockModel.parse("NASDAQ:NVDA"),
        StockModel.parse("NASDAQ:TTD"),
        StockModel.parse("NASDAQ:ZS"),
        StockModel.parse("NASDAQ:DOCU"),
        StockModel.parse("NYSE:BABA"),
        StockModel.parse("NASDAQ:DDOG")
    ]

    # symbols = list(get_all_stocks())
    # symbols = list(filter(lambda a: a.exchange!='NYSE', symbols))
    print(symbols)
    # for stock in symbols:
    #     save_to_file(stock)
    with Pool(5) as p:
        p.map(save_to_file, tqdm(symbols))

    print('Exit')


if __name__ == '__main__':
    main()
