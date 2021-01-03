#Author: Anita Ly
#Date: January 3, 2020
#Description: This program uses the GoogleNews module to obtain weblinks given paramters provided by the user and uses the Article module to parse and retrieve web content; the output is visualized on Streamlit

#Import Packages and Modules
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
import altair as alt
import streamlit as st

#Download the punkt dataset from nltk
nltk.download('punkt')

#Run in terminal to create + update requirements.txt
#pipreqs /Users/anita/OneDrive/Coding/Python/googlenews-api/ --force

#Run App
#streamlit run googlenews-api.py

#Config Setup for Newspaper
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
#'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
#headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
config = Config()
#config.headers = headers
config.browser_user_agent = user_agent
config.request_timeout = 10

class GoogleNewsClient(object):
    """Retrieves weblinks from GoogleNews and retrieves web content using Article from Newspaper; runs sentiment analysis on text using TextBlob"""
    def __init__(self, start, end):
        self.googlenews = GoogleNews(start=start, end=end, lang='en')

    def get_news(self, query, count):
        """Creates a dataframe of weblinks from GoogleNews using user-input parameters of some query and number of pages to scan"""
        self.googlenews.search(query)
        for page in range(1, count):
            self.googlenews.getpage(page)
            result = self.googlenews.results()
            df = pd.DataFrame(result)
        return df

    def get_articles(self, news):
        """With the weblinks from the get_news dataframe, retrieves web content from each webpage"""
        list = []
        for ind in news.index:
            dict = {}
            try:
                article = Article(news['link'][ind], config=config)
                article.download()
                article.parse()
                article.nlp()
                #dict['Reporting Date'] = news['date'][ind]
                #dict['Publish Date'] = article.publish_date
                if article.publish_date is None:
                    try:
                        date_format = datetime.datetime.strptime(news['date'][ind], "%b %d, %Y")
                        dict["Date"] = date_format
                    except:
                        current_utc = datetime.datetime.utcnow()
                        if "year" in news['date'][ind] or "years" in news['date'][ind]:
                            number = int(news['date'][ind][0])
                            delta = dateutil.relativedelta.relativedelta(years=number)
                            dict["Date"] = current_utc - delta
                        elif "month" in news['date'][ind] or "months" in news['date'][ind]:
                            number = int(news['date'][ind][0])
                            delta = dateutil.relativedelta.relativedelta(months=number)
                            dict["Date"] = current_utc - delta
                        elif "week" in news['date'][ind] or "weeks" in news['date'][ind]:
                            number = int(news['date'][ind][0])
                            delta = datetime.timedelta(number*7)
                            dict["Date"] = current_utc - delta
                        elif "day" in news['date'][ind] or "days" in news['date'][ind]:
                            number = int(news['date'][ind][0])
                            delta = datetime.timedelta(number)
                            dict["Date"] = current_utc - delta
                else:
                    dict['Date'] = article.publish_date
                dict['Media'] = news['media'][ind]
                dict['Title'] = article.title
                dict['Article'] = article.text
                dict['Summary'] = article.summary
                dict['Keywords'] = article.keywords
                dict['Link'] = news['link'][ind]
                list.append(dict)
            except:
                continue
        news_df = pd.DataFrame(list)
        news_df["Keywords"] = news_df["Keywords"].str.join(',')
        return news_df

    def get_sentiment(self, news_df):
        """Calculates polarity and sentiment of the web page's text content"""
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
    #User Inputs
    #start = input("Enter a start date in format 'MM/DD/YYYY': ")
    start = datetime.datetime.strptime(str(st.sidebar.date_input('Start Date', datetime.date(2020,1,1))),'%Y-%m-%d').strftime('%m/%d/%Y')
    #end = input("Enter an end date in format 'MM/DD/YYYY': ")
    end = datetime.datetime.strptime(str(st.sidebar.date_input('End Date')),'%Y-%m-%d').strftime('%m/%d/%Y')
    if start > end:
        st.sidebar.error("Error: End date must fall after start date")
    #count = int(input("Enter the number of pages to scan: "))
    count = int(st.sidebar.slider('Enter the number of pages to scan', 1, 10, 3))
    #keyword = input("Enter a query: ")
    keyword = st.sidebar.text_input("Enter a keyword", "Canada")
    st.sidebar.text("Note: A page has ~10 results")

    #Class Call
    api = GoogleNewsClient(start=start, end=end)
    news = api.get_news(query=keyword, count=count)
    articles = api.get_articles(news)
    sentiment = api.get_sentiment(articles)

    #sentiment.to_csv("articles.csv", index=False)
    #sentiment_group = sentiment.groupby("Media")['Polarity'].mean()
    #print(sentiment_group)
    #sentiment_group.plot.bar(x="Media", y="Mean Polarity")
    #plt.show()

    #Streamlit Setup
    st.title('Google News Parser Web App')
    st.subheader("Interested in scraping data from Google News? Use the parameters in the sidebar to continue!")
    st.text("Google News Data")

    st.dataframe(articles)
    csv = articles.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download = news_data.csv>Download CSV File</a> (click and save as &lt;filename&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)

    keywords = articles["Keywords"].tolist()
    keywords_list = []
    for string in keywords:
        words = string.split(',')
        keywords_list.append(words)
    words_list = []
    for sublist in keywords_list:
        for item in sublist:
            words_list.append(item)
    unique_words_set = set(words_list)
    word_count = len(words_list)

    unique_words_dict = {}
    for word in unique_words_set:
        count = words_list.count(word)
        unique_words_dict[word] = count

    unique_words_df = pd.DataFrame(list(unique_words_dict.items()), columns=["Word", "Count"])
    unique_words_df = unique_words_df.sort_values(by=["Count"], ascending=False)
    unique_words_df["Percent"] = unique_words_df["Count"]/word_count
    unique_words_df["Percent"] = unique_words_df["Percent"].astype(float).map("{:.2%}".format)
    st.text("Keyword Count Data")
    words_chart = alt.Chart(unique_words_df).mark_bar().encode(x=alt.X("Word", sort="-y"), y=alt.Y("Count")).transform_window(rank='rank(Count)', sort=[alt.SortField("Count", order="descending")]).transform_filter((alt.datum.rank < 10)).properties(width=600, height=300)

    col1, col2 = st.beta_columns([4,3])
    with col1:
        with st.beta_container():
            st.altair_chart(words_chart, use_container_width=True)
    with col2:
        st.dataframe(unique_words_df)

    #Word Cloud
    #wordcloud = WordCloud().generate(" ".join(wordcloud_list))
    #plt.imshow(wordcloud, interpolation='bilinear')
    #plt.axis("off")
    #fig.savefig('wordcloud.png')
    #st.pyplot()

if __name__ == "__main__":
    #Calling main function if file is ran as a script only (not as a module)
    main()