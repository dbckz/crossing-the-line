"""
Script to evaluate tweets against the Perspective API

How it's used:
* Loads "tweets.csv" files according to 'root_path' and 'day_paths' vars
* Sends one tweet at a time to the API
* Sleeps for 1 second between requests due to API rate-limit
* Appends results to perspective_processed_tweets.csv after every 50 tweets, so that not all progress is lost if the
  script were to die midway through processing a file
"""
import os
import time

import numpy as np
import pandas as pd
from googleapiclient import discovery


def get_perspective_client(api_key):
    return discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=api_key,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )


def query_perspective(client, text, tweet_id, logfile):
    analyze_request = {
        'comment': {
            'text': text
        },
        'requestedAttributes': {
            'TOXICITY': {},
            'SEVERE_TOXICITY': {},
            'IDENTITY_ATTACK': {},
            'INSULT': {},
            'THREAT': {},
            'SEXUALLY_EXPLICIT': {}
        }
    }
    try:
        response = client.comments().analyze(body=analyze_request).execute()
        toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
        severe_toxicity_score = response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
        identity_attack_score = response['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value']
        insult_score = response['attributeScores']['INSULT']['summaryScore']['value']
        threat_score = response['attributeScores']['THREAT']['summaryScore']['value']
        sexually_explicit_score = response['attributeScores']['SEXUALLY_EXPLICIT']['summaryScore']['value']
        return {
            "toxicity_score": toxicity_score,
            "severe_toxicity_score": severe_toxicity_score,
            "identity_attack_score": identity_attack_score,
            "insult_score": insult_score,
            "threat_score": threat_score,
            "sexually_explicit_score": sexually_explicit_score,
            "error": ""
        }
    except Exception as e:
        with open(logfile, 'a') as f:
            f.write(f"{time.ctime()}: EXCEPTION. Tweet Id: {tweet_id}: {e}")
            f.write('\n')
        print(f"EXCEPTION. Tweet Id: {tweet_id}: {e}")
        if ('reason' in e.error_details[0] and e.error_details[0]['reason'] == 'RATE_LIMIT_EXCEEDED'):
            with open(logfile, 'a') as f:
                sleeptime = 70
                f.write(f"{time.ctime()}: Sleeping for {sleeptime} seconds")
                f.write('\n')
            print(f"Sleeping for {sleeptime} seconds")
            time.sleep(70)
            return query_perspective(client, text, tweet_id, logfile)
        return {
            "toxicity_score": -1,
            "severe_toxicity_score": -1,
            "identity_attack_score": -1,
            "insult_score": -1,
            "threat_score": -1,
            "sexually_explicit_score": -1,
            "error": "ERROR"
        }


def process_tweet(tweet, perspective_client, output_dataframe, logfile):
    data = query_perspective(perspective_client, tweet['tweet_text'], tweet['tweet_id'], logfile)
    output_dataframe.loc[tweet['tweet_id']] = [
        tweet['tweet_id'],
        data['toxicity_score'],
        data['severe_toxicity_score'],
        data['identity_attack_score'],
        data['insult_score'],
        data['threat_score'],
        data['sexually_explicit_score'],
        data['error']
    ]


def process_day(directory):
    logfile = directory + "/perspective_error_log.txt"
    progress_logfile = directory + "/perspective_progress_log.txt"

    with open(progress_logfile, 'a') as f:
        f.write(f"{time.ctime()}: Starting processing for {directory}")
        f.write('\n')
    print(f"Starting processing for {directory}")

    # Load tweet CSV file
    in_csv = directory + "/tweets.csv"
    out_csv = directory + "/perspective_processed_tweets.csv"

    # Delete existing output file if it exists
    if os.path.exists(out_csv):
        os.remove(out_csv)

    number_lines = sum(1 for row in (open(in_csv)))
    chunk_size = 50

    tweets_remaining = number_lines - 1

    with open(progress_logfile, 'a') as f:
        f.write(f"{time.ctime()}: Number of tweets: {tweets_remaining}")
        f.write('\n')
    print(f"Number of tweets: {tweets_remaining}")

    for i in range(0, number_lines, chunk_size):
        start = time.time()
        in_tweets = pd.read_csv(in_csv,
                                header=0,
                                nrows=chunk_size,  # number of rows to read at each loop
                                skiprows=range(1, i))  # skip rows that have been read
        if (i == 0):
            print(f"Loaded first {len(in_tweets.index)} tweets.")

        out_tweets = pd.DataFrame(
            columns=["tweet_id", "toxicity_score", "severe_toxicity_score", "identity_attack_score", "insult_score",
                     "threat_score", "sexually_explicit_score", "error"])

        # Do processing for tweet
        for _, row in in_tweets.iterrows():
            process_tweet(row, perspective_client, out_tweets, logfile)
            time.sleep(1)  # Sleep due to 1 req/second limit on Perspective API

        # Ensure tweet_id written as int
        new_dtypes = {
            "tweet_id": int,
            "toxicity_score": np.float64,
            "severe_toxicity_score": np.float64,
            "identity_attack_score": np.float64,
            "insult_score": np.float64,
            "threat_score": np.float64,
            "sexually_explicit_score": np.float64,
            "error": str
        }
        out_tweets = out_tweets.astype(new_dtypes)

        if (i == 0):
            out_tweets.to_csv(out_csv,
                              index=False,
                              header=True,
                              mode='a',  # append data to csv file
                              chunksize=chunk_size)  # size of data to append for each loop
        else:
            out_tweets.to_csv(out_csv,
                              index=False,
                              header=False,
                              mode='a',  # append data to csv file
                              chunksize=chunk_size)  # size of data to append for each loop

        tweets_remaining = tweets_remaining - len(out_tweets.index)
        msg = f"Processed {len(out_tweets.index)} tweets in {time.time() - start} seconds. {tweets_remaining} tweets remaining."
        with open(progress_logfile, 'a') as f:
            f.write(f"{time.ctime()}: {msg}")
            f.write('\n')
        print(msg)

    with open(progress_logfile, 'a') as f:
        f.write(f"{time.ctime()}: Completed processing for {directory}")
        f.write('\n')
    print(f"Completed processing for {directory}")


if __name__ == "__main__":
    root_path = "/Users/davebuckley/Documents/Kings/Dissertation/dissertation/data_collection"

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
    # Auth to Perspective API
    print("Connecting to Perspective API")
    API_KEY = os.getenv("PERSPECTIVE_API_KEY")
    perspective_client = get_perspective_client(API_KEY)
    print("Connected to Perspective API")

    for day in day_paths:
        process_day(root_path + day)
    print("All completed")
