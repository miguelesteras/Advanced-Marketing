# modified from https://python.plainenglish.io/scraping-tweets-with-tweepy-python-59413046e788
# and https://github.com/gabrielpreda/covid-19-tweets

import math
import tweepy
import pandas as pd
import time
from pathlib import Path


def scrap_tweets(con: tweepy.API,
                 search_words: list,
                 date_since: str,
                 path: Path,
                 lang: str = "en",
                 n_tweets: int = 2000,
                 n_runs: int = 20):
    """Define a for-loop to generate tweets at regular intervals

    :param con:
    :param search_words:
    :param date_since:
    :param path:
    :param lang:
    :param n_tweets:
    :param n_runs:
    :return:
    """
    if len(search_words) > 1:
        n_runs_per_word = math.ceil(n_runs / len(search_words))
        for word in search_words:
            scrap_tweets(con=con,
                         search_words=list(word),
                         date_since=date_since,
                         path=path,
                         n_tweets=n_tweets,
                         n_runs=n_runs_per_word)

    for i in range(n_runs):
        tweets = tweepy.Cursor(con.search,
                               q=f'{search_words[0]} -filter:retweets',
                               lang=lang,
                               since=date_since).items(n_tweets)
        tweet_list = [tweet for tweet in tweets]

        tweets_df = pd.DataFrame()
        for tweet in tweet_list:
            hashtags = []
            try:
                for hashtag in tweet.entities["hashtags"]:
                    hashtags.append(hashtag["text"])
                text = con.get_status(id=tweet.id, tweet_mode='extended').full_text
            except AttributeError:
                text = tweet.full_text
            tweets_df = tweets_df.append(pd.DataFrame(
                {
                    'user_name': tweet.user.name,
                    'user_location': tweet.user.location,
                    'user_description': tweet.user.description,
                    'user_created': tweet.user.created_at,
                    'user_n_followers': tweet.user.followers_count,
                    'user_n_friends': tweet.user.friends_count,
                    'user_n_favourites': tweet.user.favourites_count,
                    'user_verified': tweet.user.verified,
                    'tweet_created': tweet.created_at,
                    'text': text,
                    'hashtags': [
                        hashtags if hashtags else None],
                    'source': tweet.source,
                    'is_retweet': tweet.retweeted}, index=tweet.id))

        # merge with previous df and save
        filename = f"tweets_{search_words[0][1:]}.csv"
        old_df = pd.read_pkl(path / filename)
        df = pd.concat([old_df, tweets_df])
        df.drop_duplicates(subset=["user_name", "date", "text"], inplace=True)
        df.to_pkl(path / filename)
        if i < (n_runs - 1):
            time.sleep(920)  # 15 minute sleep time
    print('Scraping has completed!')
    #
    # # Define a pandas dataframe to store the date:
    # db_tweets = pd.DataFrame(columns=['username', 'acctdesc', 'location', 'following',
    #                                   'followers', 'totaltweets', 'usercreatedts',
    #                                   'tweetcreatedts',
    #                                   'retweetcount', 'text', 'hashtags']
    #                          )
    # for i in range(0, n_runs):
    #     # We will time how long it takes to scrape tweets for each run:
    #     start_run = time.time()
    #
    #     # Collect tweets using the Cursor object
    #     # .Cursor() returns an object that you can loop over to access the data.
    #     # Each item in the iterator has tweet attributes:
    #     #   user.screen_name - twitter handle
    #     #   user.description - description of account
    #     #   user.location - where is he tweeting from
    #     #   user.friends_count - no. of other users that user is following (following)
    #     #   user.followers_count - no. of other users who are following this user (followers)
    #     #   user.statuses_count - total tweets by user
    #     #   user.created_at - when the user account was created
    #     #   created_at - when the tweet was created
    #     #   retweet_count - no. of retweets
    #     #   retweeted_status.full_text - full text of the tweet
    #     #   tweet.entities['hashtags'] - hashtags in the tweet
    #
    #     tweets = tweepy.Cursor(con.search,
    #                            q=' OR '.join(search_words) + ' -filter:retweets',
    #                            lang="en",
    #                            since=date_since,
    #                            tweet_mode='extended').items(n_tweets)
    #     # Store these tweets into a python list
    #     tweet_list = [tweet for tweet in tweets]
    #
    #     # Begin scraping the tweets individually:
    #     tweet_count = 0
    #     for tweet in tweet_list:  # Pull the values
    #         username = tweet.user.screen_name
    #         acctdesc = tweet.user.description
    #         location = tweet.user.location
    #         following = tweet.user.friends_count
    #         followers = tweet.user.followers_count
    #         totaltweets = tweet.user.statuses_count
    #         usercreatedts = tweet.user.created_at
    #         tweetcreatedts = tweet.created_at
    #         retweetcount = tweet.retweet_count
    #         hashtags = tweet.entities['hashtags']
    #         try:
    #             text = tweet.retweeted_status.full_text
    #         except AttributeError:  # Not a Retweet
    #             text = tweet.full_text
    #         # Add the 11 variables to the empty list - ith_tweet:
    #         ith_tweet = [username, acctdesc, location, following, followers, totaltweets,
    #                      usercreatedts, tweetcreatedts, retweetcount, text,
    #                      hashtags]
    #         # Append to dataframe - db_tweets
    #         db_tweets.loc[len(db_tweets)] = ith_tweet
    #         # increase counter - noTweets
    #         tweet_count += 1
    #
    #     # Run ended:
    #     end_run = time.time()
    #     duration_run = round((end_run - start_run) / 60, 2)
    #
    #     print('no. of tweets scraped for run {} is {}'.format(i + 1, tweet_count))
    #     print('time take for {} run to complete is {} min'.format(i + 1, duration_run))
    #     time.sleep(920)  # 15 minute sleep time
    #
    # # Once all runs have completed, save them to a single csv file:
    # db_tweets.to_pickle(filename.with_suffix('.pkl'))
    # print('Scraping has completed!')


if __name__ == '__main__':
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
        print("Authentication OK")
    except tweepy.TweepError:
        print("Error during authentication")

    search = ["#rueda", "#verdejo", "#rioja", "#riberadeduero", "#txakoli", "#somontano"]
    since = "2018-01-01"
    dir_name = Path(f"notebooks/data/twitter/")

    scrap_tweets(con=api, search_words=search, date_since=since, path=dir_name)
