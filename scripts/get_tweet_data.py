"""
Script to scrape data from the Twitter Filter Stream API.

This script was adapted from https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/870849de33222c429ec3e5f2e8ca1b424cb25e5f/Filtered-Stream/filtered_stream.py
Logging and a retry mechanism have been added, to avoid the program dying whenever there is an error or disconnect
from the API.

How it's used:
* The BEARER_TOKEN env variable must be set to authenticate to the API
* Raw JSON data returned by API written to "tweets.json" file in the working directory
* Logging messages written to "log.txt" file in the working directory

Tech debt:
* The 'tweets_remaining' var is used to track how many tweets are remaining in the user's Twitter limit, which is
  500,000 per month for normal developer access. This is currently hardcoded in the script, and must be manually
  updated whenever the script is restarted if the log messages are to accurately reflect how close you are to the limit.
* The filter rules are hardcoded in the 'set_rules' function. Ideally these would be set more dynamically or by loading
  from a configuration file.
"""
import json
import os
import queue
import sys
import threading
import time

import requests
from urllib3.exceptions import ProtocolError


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers):
    sample_rules = []

    # Belgium
    sample_rules.append({
        "value": "(to:thibautcourtois OR to:AlderweireldTob OR to:thomasvermaelen OR to:JanVertonghen OR to:axelwitsel28 OR to:DeBruyneKev OR to:CarrascoY21 OR to:dries_mertens14 OR to:ThomMills OR to:chrisbenteke OR to:NChadli OR to:mbatshuayi OR to:JeremyDoku OR to:RomeluLukaku9 OR to:hazardeden10 OR to:SMignolet OR to:HazardThorgan8 OR to:LTrossard OR to:dennispraet) lang:en -is:retweet",
        "tag": "belgium_replies"})
    sample_rules.append({
        "value": "(@thibautcourtois OR @AlderweireldTob OR @thomasvermaelen OR @JanVertonghen OR @axelwitsel28 OR @DeBruyneKev OR @CarrascoY21 OR @dries_mertens14 OR @ThomMills OR @chrisbenteke OR @NChadli OR @mbatshuayi OR @JeremyDoku OR @RomeluLukaku9 OR @hazardeden10 OR @SMignolet OR @HazardThorgan8 OR @LTrossard OR @dennispraet) lang:en -is:retweet",
        "tag": "belgium_mentions"})

    # Netherlands
    sample_rules.append({
        "value": "(@joel_veltman OR @mdeligt_04 OR @NathanAke OR @Stefandevrij OR @LuukdeJong9 OR @QPromes OR @pvanaanholt OR @TimKrul OR @DavyKlaassen OR @Dirono OR @RGravenberch OR @BlindDaley OR @DeJongFrenkie21 OR @DenzelJMD2 OR @GWijnaldum OR @Memphis) lang:en -is:retweet",
        "tag": "netherlands_mentions"})
    sample_rules.append({
        "value": "(to:joel_veltman OR to:mdeligt_04 OR to:NathanAke OR to:Stefandevrij OR to:LuukdeJong9 OR to:QPromes OR to:pvanaanholt OR to:TimKrul OR to:DavyKlaassen OR to:Dirono OR to:RGravenberch OR to:BlindDaley OR to:DeJongFrenkie21 OR to:DenzelJMD2 OR to:GWijnaldum OR to:Memphis) lang:en -is:retweet",
        "tag": "netherlands_replies"})

    # England
    sample_rules.append({
        "value": "(to:JPickford1 OR to:kylewalker2 OR to:LukeShaw23 OR to:_DeclanRice OR to:HarryMaguire93 OR to:JackGrealish OR to:JHenderson OR to:HKane OR to:sterling7 OR to:MarcusRashford OR to:trippier2 OR to:deanhenderson OR to:Kalvinphillips OR to:OfficialTM_3 OR to:Sanchooo10 OR to:CalvertLewin14 OR to:masonmount_10 OR to:PhilFoden OR to:BenChilwell OR to:ben6white OR to:samjohnstone50 OR to:reecejames_24 OR to:BukayoSaka87 OR to:BellinghamJude) lang:en -is:retweet",
        "tag": "england_replies"})
    sample_rules.append({
        "value": "(@JPickford1 OR @kylewalker2 OR @LukeShaw23 OR @_DeclanRice OR @HarryMaguire93 OR @JackGrealish OR @JHenderson OR @HKane OR @sterling7 OR @MarcusRashford OR @trippier2 OR @deanhenderson OR @Kalvinphillips OR @OfficialTM_3 OR @Sanchooo10 OR @CalvertLewin14 OR @masonmount_10 OR @PhilFoden OR @BenChilwell OR @ben6white OR @samjohnstone50 OR @reecejames_24 OR @BukayoSaka87 OR @BellinghamJude) lang:en -is:retweet",
        "tag": "england_mentions"})

    # Scotland
    sample_rules.append({
        "value": "(@MarshallDavid23 OR @sodonnell15 OR @andrewrobertso5 OR @mctominay10 OR @granthanley5 OR @kierantierney1 OR @jmcginn7 OR @Callummcgregor8 OR @Lyndon_Dykes OR @CheAdams_ OR @CraigGordon01 OR @declang31 OR @LiamCooper__ OR @10DavidTurnbull OR @kevinnisbet16 OR @np4tterson OR @billygilmourrr OR @Jack_Hendry2 OR @Scottmckenna3) lang:en -is:retweet",
        "tag": "scotland_mentions"})
    sample_rules.append({
        "value": "(to:MarshallDavid23 OR to:sodonnell15 OR to:andrewrobertso5 OR to:mctominay10 OR to:granthanley5 OR to:kierantierney1 OR to:jmcginn7 OR to:Callummcgregor8 OR to:Lyndon_Dykes OR to:CheAdams_ OR to:CraigGordon01 OR to:declang31 OR to:LiamCooper__ OR to:10DavidTurnbull OR to:kevinnisbet16 OR to:np4tterson OR to:billygilmourrr OR to:Jack_Hendry2 OR to:Scottmckenna3) lang:en -is:retweet",
        "tag": "scotland_replies"})

    # France
    sample_rules.append({
        "value": "(@BenPavard28 OR @kimpembe_3 OR @raphaelvarane OR @clement_lenglet OR @paulpogba OR @_OlivierGiroud_ OR @KMbappe OR @CorentinTolisso OR @nglkante OR @KurtZouma OR @SteveMandanda OR @MoussaSissoko OR @LucasDigne OR @Benzema OR @AntoGriezmann OR @LucasHernandez OR @WissBenYedder OR @mmseize OR @leodubois15 OR @jkeey4 OR @MarcusThuram) lang:en -is:retweet",
        "tag": "france_mentions"})
    sample_rules.append({
        "value": "(to:BenPavard28 OR to:kimpembe_3 OR to:raphaelvarane OR to:clement_lenglet OR to:paulpogba OR to:_OlivierGiroud_ OR to:KMbappe OR to:CorentinTolisso OR to:nglkante OR to:KurtZouma OR to:SteveMandanda OR to:MoussaSissoko OR to:LucasDigne OR to:Benzema OR to:AntoGriezmann OR to:LucasHernandez OR to:WissBenYedder OR to:mmseize OR to:leodubois15 OR to:jkeey4 OR to:MarcusThuram) lang:en -is:retweet",
        "tag": "france_replies"})

    # Germany
    sample_rules.append({
        "value": "(@Manuel_Neuer OR @ToniRuediger OR @MatzeGinter OR @matshummels OR @kaihavertz29 OR @SergeGnabry OR @JamalMusiala OR @lukaskl96 OR @leongoretzka_ OR @leroy_sane OR @IlkayGuendogan OR @emrecan_ OR @esmuellert_ OR @ToniKroos OR @KeVolland OR @Bernd_Leno OR @RobinKoch25) lang:en -is:retweet",
        "tag": "germany_mentions"})
    sample_rules.append({
        "value": "(to:Manuel_Neuer OR to:ToniRuediger OR to:MatzeGinter OR to:matshummels OR to:kaihavertz29 OR to:SergeGnabry OR to:JamalMusiala OR to:lukaskl96 OR to:leongoretzka_ OR to:leroy_sane OR to:IlkayGuendogan OR to:emrecan_ OR to:esmuellert_ OR to:ToniKroos OR to:KeVolland OR to:Bernd_Leno OR to:RobinKoch25) lang:en -is:retweet",
        "tag": "germany_replies"})

    # Team accounts
    sample_rules.append({
        "value": "(to:ScotlandNT OR to:BelRedDevils OR to:OnsOranje OR to:England OR to:FrenchTeam OR to:DFB_Team_EN) lang:en -is:retweet",
        "tag": "team_accounts"})

    # Take the knee hashtags
    sample_rules.append({"value": "(#BooTheKnee OR #TakeTheKnee) lang:en", "tag": "theknee"})

    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=created_at,geo,lang,in_reply_to_user_id,public_metrics,source&expansions=author_id,geo.place_id&user.fields=created_at,description,location,public_metrics&place.fields=country_code,name",
        headers=headers, stream=True,
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            tweet_queue.put(response_line)


def tweet_processing_thread():
    tweets_remaining = 500000
    while True:
        item = tweet_queue.get()
        json_response = json.loads(item)
        with open('tweets.json', 'a') as outfile:
            json.dump(json_response, outfile)
            outfile.write('\n')
        tweets_remaining -= 1
        if tweets_remaining % 100 == 0:
            print(f"{time.ctime()}: {tweets_remaining} tweets remaining")
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: {tweets_remaining} tweets remaining")
                f.write('\n')
        tweet_queue.task_done()


if __name__ == "__main__":
    bearer_token = os.getenv('BEARER_TOKEN')
    headers = create_headers(bearer_token)
    rules = get_rules(headers)
    delete = delete_all_rules(headers, rules)
    set = set_rules(headers)

    logfile = "log.txt"

    tweet_queue = queue.Queue()
    thread = threading.Thread(target=tweet_processing_thread)
    thread.daemon = True
    thread.start()

    with open(logfile, 'a') as f:
        print(f"{time.ctime()}: Script started...")
        f.write(f"{time.ctime()}: Script started...")
        f.write('\n')

    while True:
        try:
            get_stream(headers)
        except KeyboardInterrupt:
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: Keyboard interrupt")
                f.write('\n')
            sys.exit(0)
        except ProtocolError as e:
            print("Protocol Error")
            print(f"{time.ctime()}: {e}")
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: Protocol Error")
                f.write('\n')
                f.write(f"{time.ctime()}: {e}")
                f.write('\n')
            time.sleep(5)
            continue
        except ValueError as e:
            print(f"{time.ctime()}: Value Error")
            f.write('\n')
            print(f"{time.ctime()}: {e}")
            f.write('\n')
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: Value Error")
                f.write('\n')
                f.write(f"{time.ctime()}: {e}")
                f.write('\n')
            time.sleep(5)
            continue
        except Exception as e:
            print(f"{time.ctime()}: Exception")
            print(f"{time.ctime()}: {e}")
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: Exception")
                f.write('\n')
                f.write(f"{time.ctime()}: {e}")
                f.write('\n')
            time.sleep(5)
            continue
        except:
            print(f"{time.ctime()}: Unknown error.")
            with open(logfile, 'a') as f:
                f.write(f"{time.ctime()}: Unknown Error")
                f.write('\n')
            time.sleep(5)
            continue
