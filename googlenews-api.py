from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config
import pandas as pd
import nltk
from textblob import TextBlob
import matplotlib.pyplot as plt
import time
import datetime
import base64
import streamlit as st

#Remember to download the punkt dataset from nltk
nltk.download('punkt')

#Remember to run pipreqs /Users/anita/OneDrive/Coding/Python/googlenews-api/ in terminal

#Run App
#streamlit run googlenews-api.py

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
        news_df["Keywords"] = news_df["Keywords"].str.join(',')
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
    #start = input("Enter a start date in format 'MM/DD/YYYY': ")
    #end = input("Enter an end date in format 'MM/DD/YYYY': ")
    start = datetime.datetime.strptime(str(st.sidebar.date_input('Start Date')),'%Y-%m-%d').strftime('%m/%d/%Y')
    end = datetime.datetime.strptime(str(st.sidebar.date_input('End Date')),'%Y-%m-%d').strftime('%m/%d/%Y')
    if start > end:
        st.sidebar.error("Error: End date must fall after start date")
    #count = int(input("Enter the number of pages to scan: "))
    count = int(st.sidebar.slider('Enter the number of pages to scan', 1, 10, 3))
    #keyword = input("Enter a query: ")
    keyword = st.sidebar.text_input("Enter a keyword", "winter")
    api = GoogleNewsClient(start=start, end=end)
    news = api.get_news(query=keyword, count=count)
    articles = api.get_articles(news)
    sentiment = api.get_sentiment(articles)
    sentiment.to_csv("articles.csv", index=False)
    #news.to_csv("news.csv", index=False)
    #sentiment_group = sentiment.groupby("Media")['Polarity'].mean()
    #print(sentiment_group)
    #sentiment_group.plot.bar(x="Media", y="Mean Polarity")
    #plt.show()

    st.title('Google News Parser Web App')
    st.subheader("Interested in scraping data from Google News? Use the parameters in the sidebar to continue!")
    st.text("Google News Data")
    #tweet_df = pd.DataFrame(tweets)
    st.dataframe(articles)

    csv = articles.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download = news_data.csv>Download CSV File</a> (click and save as &lt;filename&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)

    keyword_list = articles["Keywords"].tolist()
    keywords = []
    for string in keyword_list:
        words = string.split(',')
        keywords.append(words)
    wordcloud_list = []
    for sublist in keywords:
        for item in sublist:
            wordcloud_list.append(item)
    #wordcloud = WordCloud().generate(" ".join(wordcloud_list))
    #plt.imshow(wordcloud, interpolation='bilinear')
    #plt.axis("off")
    #fig.savefig('wordcloud.png')
    #st.pyplot()

if __name__ == "__main__":
    #Calling main function
    main()