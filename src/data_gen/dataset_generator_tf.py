import tensorflow as tf
from tqdm import tqdm
from src.data_gen.dataset_generator import generate_sliced_data_set_v1, generate_sliced_data_set_v2, parse_loaded_data

def get_dataset(stock):
    try:
        def _gen():
            data = generate_sliced_data_set_v1(stock)
            example = next(data)
            keys = set(example.keys())
            raw = {"date", "close", "open", "date", "high", "low", "volume", "profit", "loss"}
            x_keys = list(keys - raw)
            x_keys.sort()
            result = tqdm(map(lambda a: parse_loaded_data(a, x_keys, 'profit'), data))
            return result

        dataset = tf.data.Dataset.from_generator(_gen,  output_signature=(
                  tf.TensorSpec(shape=(43, 240), dtype=tf.float32),
                  tf.TensorSpec(shape=(1,), dtype=tf.int8)))
        return dataset

    except Exception as e:
        return e, None