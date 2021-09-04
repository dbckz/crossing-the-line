"""
Script to preprocess the JSON data retrieved from the API

How it's used:
* Reads "tweets.json" files in directories specified by 'root_dir' and 'directories' variables
* Loads each JSON file into a dataframe
* Drops unwanted columns
* Renames columns to more user-friendly versions
* Drops duplicate rows
* Extracts author and place fields from nested JSON
* Removes tabs, carriage return, and new line chars
* Writes resulting table to a "tweets.csv" file
"""
import json

import pandas as pd


def author_mapping_function(row, key, key2=None):
    for user in row["accounts_mentioned"]:
        if (user['id'] == row['author_id']):
            if key2 is None:
                if key in user:
                    return user[key]
                else:
                    return None
            else:
                if (key in user) and (key2 in user[key]):
                    return user[key][key2]
                else:
                    return None
    raise Exception(f"Error mapping key: {key}")


def place_mapping_function(row, key, key2=None):
    # Hack to skip if there is no places key in the tweet
    if "includes.places" not in row:
        return None
    if isinstance(row["includes.places"], float):
        return None

    for place in row["includes.places"]:
        if (place['id'] == row['geo_place_id']):
            if key2 is None:
                if key in place:
                    return place[key]
                else:
                    return None
            else:
                if (key in place) and (key2 in place[key]):
                    return place[key][key2]
                else:
                    return None
    raise Exception(f"Error mapping key: {key}")


def convert(input_dir):
    print(f"Reading JSON file for {input_dir}")

    input_file = input_dir + "/tweets.json"

    data = []
    with open(input_file, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    print("Normalizing JSON...")
    df = pd.json_normalize(data)

    print("Dropping columns...")

    df.drop('matching_rules', axis=1, inplace=True, errors="ignore")
    df.drop('data.public_metrics.retweet_count', axis=1, inplace=True, errors="ignore")
    df.drop('data.public_metrics.reply_count', axis=1, inplace=True, errors="ignore")
    df.drop('data.public_metrics.like_count', axis=1, inplace=True, errors="ignore")
    df.drop('data.public_metrics.quote_count', axis=1, inplace=True, errors="ignore")
    df.drop('data.source', axis=1, inplace=True, errors="ignore")
    df.drop('data.geo.coordinates.type', axis=1, inplace=True, errors="ignore")
    df.drop('data.withheld.copyright', axis=1, inplace=True, errors="ignore")
    df.drop('data.withheld.country_codes', axis=1, inplace=True, errors="ignore")
    df.drop('data.withheld.scope', axis=1, inplace=True, errors="ignore")
    df.drop('errors', axis=1, inplace=True, errors="ignore")

    print("Renaming columns...")
    df.rename(columns={'data.author_id': 'author_id',
                       'data.created_at': 'created_at',
                       'data.id': 'tweet_id',
                       'data.in_reply_to_user_id': 'in_reply_to_user_id',
                       'data.lang': 'lang',
                       'data.text': 'tweet_text',
                       'data.geo.place_id': 'geo_place_id',
                       'data.geo.coordinates.coordinates': 'geo_coordinates',
                       'includes.users': 'accounts_mentioned'},
              inplace=True)

    print("Dropping any errored rows...")
    df.dropna(subset=['tweet_id'], inplace=True)
    print("Dropping any duplicates...")
    df.drop_duplicates(subset=['tweet_id'], inplace=True)

    print("Dropping non-English tweets...")
    df.drop(df[df.lang != "en"].index, inplace=True)

    print("Adding author_name...")
    df['author_name'] = df.apply(lambda row: author_mapping_function(row, 'name'), axis=1)
    print("Adding author_handle...")
    df['author_handle'] = df.apply(lambda row: author_mapping_function(row, 'username'), axis=1)
    print("Adding author_bio...")
    df['author_bio'] = df.apply(lambda row: author_mapping_function(row, 'description'), axis=1)
    print("Adding author_location...")
    df['author_location'] = df.apply(lambda row: author_mapping_function(row, 'location'), axis=1)
    print("Adding author_account_created_at...")
    df['author_account_created_at'] = df.apply(lambda row: author_mapping_function(row, 'created_at'), axis=1)
    print("Adding author_followers_count...")
    df['author_followers_count'] = df.apply(
        lambda row: author_mapping_function(row, 'public_metrics', 'followers_count'), axis=1)
    print("Adding author_following_count...")
    df['author_following_count'] = df.apply(
        lambda row: author_mapping_function(row, 'public_metrics', 'following_count'), axis=1)
    print("Adding author_tweet_count...")
    df['author_tweet_count'] = df.apply(lambda row: author_mapping_function(row, 'public_metrics', 'tweet_count'),
                                        axis=1)
    print("Adding geo_place_name...")
    df['geo_place_name'] = df.apply(lambda row: place_mapping_function(row, 'full_name'), axis=1)

    print("Dropping geo_place_id and includes.places...")
    df.drop('geo_place_id', axis=1, inplace=True, errors="ignore")
    df.drop('includes.places', axis=1, inplace=True, errors="ignore")

    print("Removing new line, carriage return, tab chars...")
    df.replace('\r', ' ', regex=True, inplace=True)
    df.replace('\n', ' ', regex=True, inplace=True)
    df.replace('\t', ' ', regex=True, inplace=True)
    df.replace(r'\\r', ' ', regex=True, inplace=True)
    df.replace(r'\\n', ' ', regex=True, inplace=True)
    df.replace(r'\\t', ' ', regex=True, inplace=True)

    print("Writing to CSV...")
    df.to_csv(input_dir + "/tweets.csv", index=False)

    print("Hacky replace of literal carriage returns, tabs, and new lines...")
    fin = open(input_dir + "/tweets.csv", "rt")
    data = fin.read()
    data = data.replace(r'\r', ' ')
    data = data.replace(r'\n', ' ')
    data = data.replace(r'\t', ' ')
    fin.close()
    fin = open(input_dir + "/tweets.csv", "wt")
    fin.write(data)
    fin.close()


if __name__ == "__main__":
    root_dir = "/Volumes/Untitled/dissertation/data_collection"
    directories = [
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
    for d in directories:
        convert(root_dir + d)
