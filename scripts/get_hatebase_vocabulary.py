"""
Script to download the Hatebase catalogue

How it's used:
* The HATEBASE_API_KEY env variable must be set to authenticate to the Hatebase API
* The catalogue is written to 'output_dir + "/terms.csv"'

Tech debt:
* output_dir hardcoded in the main function
* Hardcoded to only download English-language terms in get_vocabulary function

"""

import requests
import os
import pandas as pd


def get_token(api_key):
    body = {"api_key": api_key}
    auth = requests.post("https://api.hatebase.org/4-4/authenticate", data=body)
    token = auth.json()['result']['token']
    if auth.status_code == 200:
        print(f"Authed successfuly. Token: {token}.")
    return token


def get_vocabulary_page(token, page, format, language):
    body = {
        "token": token,
        "page": page,
        "format": format,
        "language": language
    }

    return requests.post("https://api.hatebase.org/4-4/get_vocabulary", data=body)


def get_vocabulary(token):
    page_1_request = get_vocabulary_page(token, 1, "json", "ENG")

    pages = page_1_request.json()["number_of_pages"]

    page_1_result = page_1_request.json()["result"]
    df = pd.json_normalize(page_1_result)

    print(f"Added {len(page_1_result)} terms from page 1.")

    if (pages > 1):
        for page in range(2, pages + 1):
            page_request = get_vocabulary_page(token, page, "json", "ENG")
            page_result = page_request.json()["result"]
            df_tmp = pd.json_normalize(page_result)
            df = df.append(df_tmp)
            print(f"Added {len(page_result)} terms from page {page}.")

    return df


if __name__ == "__main__":
    api_key = os.getenv("HATEBASE_API_KEY")
    token = get_token(api_key)

    # Set appropriately
    output_dir = "/Users/davebuckley/Documents/Kings/Dissertation/dissertation/hatebase"

    dataFrame = get_vocabulary(token)
    dataFrame.to_csv(output_dir + "/terms.csv", index=False)

