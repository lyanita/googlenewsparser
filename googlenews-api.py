from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config
import pandas as pd
import nltk
from textblob import TextBlob
import matplotlib.pyplot as plt

#Remember to download the punkt dataset from nltk
#nltk.download('punkt')

#Remember to run pipreqs /Users/anita/OneDrive/Coding/Python/googlenews-api/ in terminal

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
#'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
#headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
config = Config()
#config.headers = headers
config.browser_user_agent = user_agent
config.request_timeout = 10

class GoogleNewsClient(object):
    def __init__(self, start, end):
        self.googlenews = GoogleNews(start=start, end=end, lang='en')

    def get_news(self, query, count):
        self.googlenews.search(query)
        for page in range(1, count):
            self.googlenews.getpage(page)
            result = self.googlenews.results()
            df = pd.DataFrame(result)
        return df

    def get_articles(self, news):
        list = []
        for ind in news.index:
            dict = {}
            try:
                article = Article(news['link'][ind], config=config)
                article.download()
                article.parse()
                article.nlp()
                dict['Date'] = news['date'][ind]
                dict['Publish Date'] = article.publish_date
                dict['Media'] = news['media'][ind]
                dict['Title'] = article.title
                dict['Article'] = article.text
                dict['Summary'] = article.summary
                dict['Keywords'] = article.keywords
                list.append(dict)
            except:
                continue
        news_df = pd.DataFrame(list)
        return news_df

    def get_sentiment(self, news_df):
        sentiment = []
        polarity = []
        for ind in news_df.index:
            analysis = TextBlob(news_df['Article'][ind])
            if analysis.sentiment.polarity > 0:
                sentiment.append('positive')
                polarity.append(analysis.sentiment.polarity)
            elif analysis.sentiment.polarity == 0:
                sentiment.append('neutral')
                polarity.append(analysis.sentiment.polarity)
            else:
                sentiment.append('negative')
                polarity.append(analysis.sentiment.polarity)
        news_df["Sentiment"] = sentiment
        news_df["Polarity"] = polarity
        return news_df

def main():
    start = input("Enter a start date in format 'MM/DD/YYYY': ")
    end = input("Enter an end date in format 'MM/DD/YYYY': ")
    count = int(input("Enter the number of pages to scan: "))
    keyword = input("Enter a query: ")
    api = GoogleNewsClient(start=start, end=end)
    news = api.get_news(query=keyword, count=count)
    articles = api.get_articles(news)
    sentiment = api.get_sentiment(articles)
    sentiment.to_csv("articles.csv", index=False)
    print(news)
    print(articles)
    news.to_csv("news.csv", index=False)
    sentiment_group = sentiment.groupby("Media")['Polarity'].mean()
    print(sentiment_group)
    sentiment_group.plot.bar(x="Media", y="Mean Polarity")
    plt.show()

if __name__ == "__main__":
    #Calling main function
    main()