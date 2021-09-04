"""
Script to do a regex search of all tweets for Hatebase terms

How it's used:
* Loads "tweets.csv" files according to 'root_path' and 'day_paths' vars
* Loads Hatebase terms from 'hb_path'
* Performs regex search for matching terms
* Writes resulting table to "hatebase_processed_tweets.csv"

Tech debt:
* Incredibly over-engineered! And generally quite hacky code
* Some duplicate code which could be refactored
* I wasn't sure what threshold I would use for average_offensiveness, so did 50.0, 70.0, and 90.0
"""
import os
import re
import time

import pandas as pd
from tqdm import tqdm


def get_hatebase_matching_terms(tweet):
    terms = hb['term'].tolist()

    regex = r"\b("
    for term in terms:
        regex += term + "|"
    regex = regex[:-1]
    regex += ")" + r"\b"
    matches = re.findall(regex, tweet, flags=re.IGNORECASE)
    matches = [x.lower() for x in matches]
    over_50_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['average_offensiveness'] > 50.0]
    over_70_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['average_offensiveness'] > 70.0]
    over_90_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['average_offensiveness'] > 90.0]
    nationality_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_nationality']]
    ethnicity_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_ethnicity']]
    religion_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_religion']]
    gender_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_gender']]
    sexual_orientation_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_sexual_orientation']]
    disability_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_disability']]
    class_matches = [x for x in matches if hb.loc[hb.term == x].iloc[0]['is_about_class']]
    nationality_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_nationality']]
    ethnicity_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_ethnicity']]
    religion_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_religion']]
    gender_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_gender']]
    sexual_orientation_matches_over_50 = [x for x in over_50_matches if
                                          hb.loc[hb.term == x].iloc[0]['is_about_sexual_orientation']]
    disability_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_disability']]
    class_matches_over_50 = [x for x in over_50_matches if hb.loc[hb.term == x].iloc[0]['is_about_class']]
    nationality_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_nationality']]
    ethnicity_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_ethnicity']]
    religion_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_religion']]
    gender_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_gender']]
    sexual_orientation_matches_over_70 = [x for x in over_70_matches if
                                          hb.loc[hb.term == x].iloc[0]['is_about_sexual_orientation']]
    disability_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_disability']]
    class_matches_over_70 = [x for x in over_70_matches if hb.loc[hb.term == x].iloc[0]['is_about_class']]
    nationality_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_nationality']]
    ethnicity_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_ethnicity']]
    religion_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_religion']]
    gender_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_gender']]
    sexual_orientation_matches_over_90 = [x for x in over_90_matches if
                                          hb.loc[hb.term == x].iloc[0]['is_about_sexual_orientation']]
    disability_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_disability']]
    class_matches_over_90 = [x for x in over_90_matches if hb.loc[hb.term == x].iloc[0]['is_about_class']]

    return matches, \
           over_50_matches, \
           over_70_matches, \
           over_90_matches, \
           nationality_matches, \
           ethnicity_matches, \
           religion_matches, \
           gender_matches, \
           sexual_orientation_matches, \
           disability_matches, \
           class_matches, \
           nationality_matches_over_50, \
           ethnicity_matches_over_50, \
           religion_matches_over_50, \
           gender_matches_over_50, \
           sexual_orientation_matches_over_50, \
           disability_matches_over_50, \
           class_matches_over_50, \
           nationality_matches_over_70, \
           ethnicity_matches_over_70, \
           religion_matches_over_70, \
           gender_matches_over_70, \
           sexual_orientation_matches_over_70, \
           disability_matches_over_70, \
           class_matches_over_70, \
           nationality_matches_over_90, \
           ethnicity_matches_over_90, \
           religion_matches_over_90, \
           gender_matches_over_90, \
           sexual_orientation_matches_over_90, \
           disability_matches_over_90, \
           class_matches_over_90, \
           len(matches), \
           len(over_50_matches), \
           len(over_70_matches), \
           len(over_90_matches), \
           len(nationality_matches), \
           len(ethnicity_matches), \
           len(religion_matches), \
           len(gender_matches), \
           len(sexual_orientation_matches), \
           len(disability_matches), \
           len(class_matches), \
           len(nationality_matches_over_50), \
           len(ethnicity_matches_over_50), \
           len(religion_matches_over_50), \
           len(gender_matches_over_50), \
           len(sexual_orientation_matches_over_50), \
           len(disability_matches_over_50), \
           len(class_matches_over_50), \
           len(nationality_matches_over_70), \
           len(ethnicity_matches_over_70), \
           len(religion_matches_over_70), \
           len(gender_matches_over_70), \
           len(sexual_orientation_matches_over_70), \
           len(disability_matches_over_70), \
           len(class_matches_over_70), \
           len(nationality_matches_over_90), \
           len(ethnicity_matches_over_90), \
           len(religion_matches_over_90), \
           len(gender_matches_over_90), \
           len(sexual_orientation_matches_over_90), \
           len(disability_matches_over_90), \
           len(class_matches_over_90)


def process_day(directory):
    # Load tweet CSV file
    in_csv = directory + "/tweets.csv"
    out_csv = directory + "/hatebase_processed_tweets.csv"

    # Delete existing ouput file if it exists
    if os.path.exists(out_csv):
        os.remove(out_csv)

    in_tweets = pd.read_csv(in_csv)

    tqdm.pandas()

    start = time.time()
    print(f"Starting hatebase processing for {directory}...")

    in_tweets['matching_hatebase_terms'], \
    in_tweets['matching_hatebase_terms_over_50'], \
    in_tweets['matching_hatebase_terms_over_70'], \
    in_tweets['matching_hatebase_terms_over_90'], \
    in_tweets['matching_hatebase_terms_nationality'], \
    in_tweets['matching_hatebase_terms_ethnicity'], \
    in_tweets['matching_hatebase_terms_religion'], \
    in_tweets['matching_hatebase_terms_gender'], \
    in_tweets['matching_hatebase_terms_sexual_orientation'], \
    in_tweets['matching_hatebase_terms_disability'], \
    in_tweets['matching_hatebase_terms_class'], \
    in_tweets['matching_hatebase_terms_nationality_over_50'], \
    in_tweets['matching_hatebase_terms_ethnicity_over_50'], \
    in_tweets['matching_hatebase_terms_religion_over_50'], \
    in_tweets['matching_hatebase_terms_gender_over_50'], \
    in_tweets['matching_hatebase_terms_sexual_orientation_over_50'], \
    in_tweets['matching_hatebase_terms_disability_over_50'], \
    in_tweets['matching_hatebase_terms_class_over_50'], \
    in_tweets['matching_hatebase_terms_nationality_over_70'], \
    in_tweets['matching_hatebase_terms_ethnicity_over_70'], \
    in_tweets['matching_hatebase_terms_religion_over_70'], \
    in_tweets['matching_hatebase_terms_gender_over_70'], \
    in_tweets['matching_hatebase_terms_sexual_orientation_over_70'], \
    in_tweets['matching_hatebase_terms_disability_over_70'], \
    in_tweets['matching_hatebase_terms_class_over_70'], \
    in_tweets['matching_hatebase_terms_nationality_over_90'], \
    in_tweets['matching_hatebase_terms_ethnicity_over_90'], \
    in_tweets['matching_hatebase_terms_religion_over_90'], \
    in_tweets['matching_hatebase_terms_gender_over_90'], \
    in_tweets['matching_hatebase_terms_sexual_orientation_over_90'], \
    in_tweets['matching_hatebase_terms_disability_over_90'], \
    in_tweets['matching_hatebase_terms_class_over_90'], \
    in_tweets['matching_hatebase_terms_count'], \
    in_tweets['matching_hatebase_terms_over_50_count'], \
    in_tweets['matching_hatebase_terms_over_70_count'], \
    in_tweets['matching_hatebase_terms_over_90_count'], \
    in_tweets['matching_nationality_count'], \
    in_tweets['matching_ethnicity_count'], \
    in_tweets['matching_religion_count'], \
    in_tweets['matching_gender_count'], \
    in_tweets['matching_sexual_orientation_count'], \
    in_tweets['matching_disability_count'], \
    in_tweets['matching_class_count'], \
    in_tweets['matching_nationality_count_over_50'], \
    in_tweets['matching_ethnicity_count_over_50'], \
    in_tweets['matching_religion_count_over_50'], \
    in_tweets['matching_gender_count_over_50'], \
    in_tweets['matching_sexual_orientation_count_over_50'], \
    in_tweets['matching_disability_count_over_50'], \
    in_tweets['matching_class_count_over_50'], \
    in_tweets['matching_nationality_count_over_70'], \
    in_tweets['matching_ethnicity_count_over_70'], \
    in_tweets['matching_religion_count_over_70'], \
    in_tweets['matching_gender_count_over_70'], \
    in_tweets['matching_sexual_orientation_count_over_70'], \
    in_tweets['matching_disability_count_over_70'], \
    in_tweets['matching_class_count_over_70'], \
    in_tweets['matching_nationality_count_over_90'], \
    in_tweets['matching_ethnicity_count_over_90'], \
    in_tweets['matching_religion_count_over_90'], \
    in_tweets['matching_gender_count_over_90'], \
    in_tweets['matching_sexual_orientation_count_over_90'], \
    in_tweets['matching_disability_count_over_90'], \
    in_tweets['matching_class_count_over_90'] = zip(
        *in_tweets['tweet_text'].progress_map(get_hatebase_matching_terms))
    print(f"Matching terms for {directory} took {time.time() - start} seconds")

    out_tweets = in_tweets[
        [
            'tweet_id',
            'matching_hatebase_terms',
            'matching_hatebase_terms_over_50',
            'matching_hatebase_terms_over_70',
            'matching_hatebase_terms_over_90',
            'matching_hatebase_terms_nationality',
            'matching_hatebase_terms_ethnicity',
            'matching_hatebase_terms_religion',
            'matching_hatebase_terms_gender',
            'matching_hatebase_terms_sexual_orientation',
            'matching_hatebase_terms_disability',
            'matching_hatebase_terms_class',
            'matching_hatebase_terms_nationality_over_50',
            'matching_hatebase_terms_ethnicity_over_50',
            'matching_hatebase_terms_religion_over_50',
            'matching_hatebase_terms_gender_over_50',
            'matching_hatebase_terms_sexual_orientation_over_50',
            'matching_hatebase_terms_disability_over_50',
            'matching_hatebase_terms_class_over_50',
            'matching_hatebase_terms_nationality_over_70',
            'matching_hatebase_terms_ethnicity_over_70',
            'matching_hatebase_terms_religion_over_70',
            'matching_hatebase_terms_gender_over_70',
            'matching_hatebase_terms_sexual_orientation_over_70',
            'matching_hatebase_terms_disability_over_70',
            'matching_hatebase_terms_class_over_70',
            'matching_hatebase_terms_nationality_over_90',
            'matching_hatebase_terms_ethnicity_over_90',
            'matching_hatebase_terms_religion_over_90',
            'matching_hatebase_terms_gender_over_90',
            'matching_hatebase_terms_sexual_orientation_over_90',
            'matching_hatebase_terms_disability_over_90',
            'matching_hatebase_terms_class_over_90',
            'matching_hatebase_terms_count',
            'matching_hatebase_terms_over_50_count',
            'matching_hatebase_terms_over_70_count',
            'matching_hatebase_terms_over_90_count',
            'matching_nationality_count',
            'matching_ethnicity_count',
            'matching_religion_count',
            'matching_gender_count',
            'matching_sexual_orientation_count',
            'matching_disability_count',
            'matching_class_count',
            'matching_nationality_count_over_50',
            'matching_ethnicity_count_over_50',
            'matching_religion_count_over_50',
            'matching_gender_count_over_50',
            'matching_sexual_orientation_count_over_50',
            'matching_disability_count_over_50',
            'matching_class_count_over_50',
            'matching_nationality_count_over_70',
            'matching_ethnicity_count_over_70',
            'matching_religion_count_over_70',
            'matching_gender_count_over_70',
            'matching_sexual_orientation_count_over_70',
            'matching_disability_count_over_70',
            'matching_class_count_over_70',
            'matching_nationality_count_over_90',
            'matching_ethnicity_count_over_90',
            'matching_religion_count_over_90',
            'matching_gender_count_over_90',
            'matching_sexual_orientation_count_over_90',
            'matching_disability_count_over_90',
            'matching_class_count_over_90'
        ]
    ].copy()

    out_tweets.to_csv(out_csv,
                      index=False,
                      header=True)


if __name__ == "__main__":
    hb_path = "/Volumes/Untitled/dissertation/hatebase/terms.csv"
    hb = pd.read_csv(hb_path)
    # Hack to make all lowercase
    hb['term'] = hb.term.str.lower()

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
