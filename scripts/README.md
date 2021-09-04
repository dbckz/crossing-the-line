# Data collection, preprocessing, Hatebase, and Perspective scripts
This directory contains the python scripts used for all "pre-analysis" activities. The scripts were executed in the following order:

1. **get_tweet_data.py**: scrapes data from the Twitter API and writes to JSON files
2. **preprocessing.py**: executes several preprocessing steps to transform data into a more user-friendly format, written to CSV files
3. **get_hatebase_vocabulary.py**: downloads the catalogue of Hatebase terms
4. **process_hatebase.py**: performs regex search of tweets for Hatebase terms
5. **process_emoji.py**: performs search of tweets for potentially offensive emojis
6. **process_perspective.py**: evaluates tweets using the Perspective API

Scripts were run on a virtual machine running Debian GNU/Linux 10 (buster), using Python 3.7.3

To install pip dependencies, run:
```
pip3 install ./requirements.txt
```
 
