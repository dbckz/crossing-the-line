"""
Script to do a search of all tweets for potentially offensive emojis

How it's used:
* Loads "tweets.csv" files according to 'root_path' and 'day_paths' vars
* Performs regex search for emojis
* Writes resulting table to "emoji.csv"
"""

import os
import time

import pandas as pd


def get_emojis(tweet):
    banana_count = tweet.count("🍌")
    monkey_count = tweet.count("🐒")
    monkey_face_count = tweet.count("🐵")
    speak_no_evil_monkey_count = tweet.count("🙊")
    hear_no_evil_monkey_count = tweet.count("🙉")
    see_no_evil_monkey_count = tweet.count("🙈")
    gorilla_count = tweet.count("🦍")
    watermelon_count = tweet.count("🍉")

    total_emoji_count = banana_count + monkey_count + monkey_face_count + speak_no_evil_monkey_count + hear_no_evil_monkey_count + see_no_evil_monkey_count + gorilla_count + watermelon_count

    return banana_count, \
           monkey_count, \
           monkey_face_count, \
           speak_no_evil_monkey_count, \
           hear_no_evil_monkey_count, \
           see_no_evil_monkey_count, \
           gorilla_count, \
           watermelon_count, \
           total_emoji_count


def process_day(directory):
    print(f"Processing for {directory}")

    in_csv = directory + "/tweets.csv"
    out_csv = directory + "/emoji.csv"

    # Delete existing ouput file if it exists
    if os.path.exists(out_csv):
        os.remove(out_csv)

    in_tweets = pd.read_csv(in_csv)
    start = time.time()

    in_tweets['banana_count'], \
    in_tweets['monkey_count'], \
    in_tweets['monkey_face_count'], \
    in_tweets['speak_no_evil_monkey_count'], \
    in_tweets['hear_no_evil_monkey_count'], \
    in_tweets['see_no_evil_monkey_count'], \
    in_tweets['gorilla_count'], \
    in_tweets['watermelon_count'], \
    in_tweets['total_emoji_count'] = zip(*in_tweets['tweet_text'].map(get_emojis))

    print(f"Matching emojis for {directory} took {time.time() - start} seconds")

    out_tweets = in_tweets[
        [
            'tweet_id',
            'banana_count',
            'monkey_count',
            'monkey_face_count',
            'speak_no_evil_monkey_count',
            'hear_no_evil_monkey_count',
            'see_no_evil_monkey_count',
            'gorilla_count',
            'watermelon_count',
            'total_emoji_count'
        ]
    ].copy()

    out_tweets.to_csv(out_csv,
                      index=False,
                      header=True)


if __name__ == "__main__":

    root_path = "/Volumes/Untitled/dissertation/data_collection"
    day_paths = [
        "/01",
        "/02",
        "/03",
        "/04",
        "/05",
        "/06",
        "/07",
        "/08",
        "/09",
        "/10",
        "/11",
        "/12",
        "/13",
        "/14",
        "/15",
        "/16",
        "/17",
        "/18",
        "/19",
        "/20",
        "/21",
        "/22",
        "/23",
        "/24",
        "/25",
        "/26",
        "/27",
        "/28",
        "/29",
        "/30",
        "/31",
        "/32",
        "/33",
        "/34",
        "/35",
        "/36"
    ]

    for day in day_paths:
        work_dir = root_path + day
        process_day(work_dir)

    print("Completed all processing")
