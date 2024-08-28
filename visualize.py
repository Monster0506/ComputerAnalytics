import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
from wordcloud import WordCloud
import networkx as nx
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Define stopwords and punctuation
stop_words = set(stopwords.words('english'))
punctuation = set(string.punctuation)
plt.rcParams["font.family"] = "Fira Code"

# Connect to the SQLite database
conn = sqlite3.connect('keylog.db')

# Load data into pandas DataFrames
df_keys = pd.read_sql_query("SELECT * FROM keylog", conn)
df_mouse_clicks = pd.read_sql_query("SELECT * FROM mouse_clicks", conn)
df_mouse_paths = pd.read_sql_query("SELECT * FROM mouse_paths", conn)
df_idle_time = pd.read_sql_query("SELECT * FROM idle_time", conn)
df_scroll_events = pd.read_sql_query("SELECT * FROM scroll_events", conn)
df_email = pd.read_sql_query("SELECT * FROM email", conn)

# Convert timestamps to datetime
df_keys['timestamp'] = pd.to_datetime(df_keys['timestamp'])
df_mouse_clicks['timestamp'] = pd.to_datetime(df_mouse_clicks['timestamp'])
df_mouse_paths['timestamp'] = pd.to_datetime(df_mouse_paths['timestamp'])
df_idle_time['timestamp'] = pd.to_datetime(df_idle_time['timestamp'])
df_scroll_events['timestamp'] = pd.to_datetime(df_scroll_events['timestamp'])
df_email['timestamp'] = pd.to_datetime(df_email['datetime'])
df_email['datetime'] = pd.to_datetime(df_email['datetime'])

# Analysis: Average fraction of each key typed
total_keys_pressed = df_keys['key'].count()
average_fraction_per_key = df_keys['key'].value_counts(
) / total_keys_pressed * 100

# Analysis: Average key hold duration
average_key_hold_duration = df_keys.groupby(
    'key')['key_hold_duration'].mean().sort_values(ascending=False)

# Analysis: Key presses per hour
df_keys['hour'] = df_keys['timestamp'].dt.hour
key_presses_per_hour = df_keys.groupby('hour').size()

# Analysis: Mouse clicks per button
mouse_clicks_per_button = df_mouse_clicks['button'].value_counts()

# Analysis: Most Common Email Subjects
top_subjects = df_email['subject'].value_counts().head(10)

# Analysis: Idle time per hour
df_idle_time['hour'] = df_idle_time['timestamp'].dt.hour
idle_time_per_hour = df_idle_time.groupby('hour')['duration'].sum()

# Analysis: Scroll events
scroll_events_per_direction = df_scroll_events['direction'].value_counts()
# Analysis: Email Volume over time
df_email['date'] = df_email['datetime'].dt.date
email_volume = df_email.groupby('date').size()

# Analysis: Key presses heatmap (hour of day vs. day of week)
df_keys['day_of_week'] = df_keys['timestamp'].dt.dayofweek
heatmap_data = df_keys.groupby(
    ['day_of_week', 'hour']).size().unstack().fillna(0)

# Analysis: Scroll events over time
df_scroll_events['hour'] = df_scroll_events['timestamp'].dt.hour
scroll_events_per_hour = df_scroll_events.groupby('hour').size()

# Analysis: Top Senders and Recipients
top_senders = df_email['sender'].value_counts().head(10)
top_recipients = df_email['recipient'].value_counts().head(10)

# Analysis: Email Subject Word Cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(
    ' '.join(df_email['subject']))

# Analysis: Email Sentiment Analysis


def get_sentiment(text):
    return TextBlob(text).sentiment.polarity


df_email['sentiment'] = df_email['body'].apply(get_sentiment)
sentiment_counts = pd.cut(df_email['sentiment'], bins=[-1, -0.1, 0.1, 1], labels=[
                          'Negative', 'Neutral', 'Positive']).value_counts()

# Analysis: Email Response Times
df_email['response_time'] = df_email.groupby(
    'sender')['datetime'].diff().dt.total_seconds() / 60
response_times = df_email['response_time'].dropna()

# Analysis: Email Topics Over Time
df_email['year_month'] = df_email['datetime'].dt.to_period('M')


def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    keywords = [word for word in tokens if word.isalnum(
    ) and word not in stop_words and word not in punctuation]
    return keywords


# Apply the function to the body column and create a new column for keywords
df_email['keywords'] = df_email['body'].apply(extract_keywords)

# Convert datetime column to pandas datetime

df_email['date'] = df_email['datetime'].dt.date

# Check the modified data structure

# Flatten the keywords and create a DataFrame for keyword counts over time
keyword_counts = df_email.explode('keywords').groupby(
    ['date', 'keywords']).size().reset_index(name='count')

# Check the keyword counts data structure

# Get the top 10 most common keywords
top_keywords = keyword_counts.groupby(
    'keywords')['count'].sum().nlargest(10).index

# Filter the keyword_counts DataFrame to include only the top 10 keywords
filtered_keyword_counts = keyword_counts[keyword_counts['keywords'].isin(
    top_keywords)]


# Analysis: Email Interaction Network
email_graph = nx.from_pandas_edgelist(
    df_email, source='sender', target='recipient', create_using=nx.DiGraph())


# Analysis: Emails by Time of Day
df_email['month_year'] = df_email['datetime'].dt.to_period('M').astype(str)
df_email['hour'] = df_email['datetime'].dt.hour + \
    df_email['datetime'].dt.minute / 60

plt.figure(figsize=(10, 6))
this = average_fraction_per_key.plot(kind='bar')
for bar in this.patches:
    if bar.get_height() > 5:
        this.annotate(format(bar.get_height(), '.2f'),
                      (bar.get_x() + bar.get_width() / 2,
                       bar.get_height()), ha='center', va='center',
                      size=10, xytext=(0, 8),
                      textcoords='offset points')
plt.xlabel('Key')
plt.ylabel('Average Fraction')
plt.title('Average Fraction of Each Key Typed')
plt.show()


plt.figure(figsize=(10, 6))
this = average_key_hold_duration.plot(kind='bar')
for bar in this.patches:
    if bar.get_height() > .17:
        this.annotate(format(bar.get_height(), '.2f'),
                      (bar.get_x() + bar.get_width() / 2,
                       bar.get_height()), ha='center', va='center',
                      size=10, xytext=(0, 8),
                      textcoords='offset points')
plt.xlabel('Key')
plt.ylabel('Average Key Hold Duration (seconds)')
plt.title('Average Key Hold Duration')
plt.show()


plt.figure(figsize=(10, 6))
this = key_presses_per_hour.plot(kind='bar')
for bar in this.patches:
    this.annotate(format(bar.get_height(), '.2f'),
                  (bar.get_x() + bar.get_width() / 2,
                   bar.get_height()), ha='center', va='center',
                  size=10, xytext=(0, 8),
                  textcoords='offset points')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Key Presses')
plt.title('Key Presses Per Hour')
plt.show()

plt.figure(figsize=(10, 6))
this = mouse_clicks_per_button.plot(kind='bar')
for bar in this.patches:
    this.annotate(format(bar.get_height(), '.2f'),
                  (bar.get_x() + bar.get_width() / 2,
                   bar.get_height()), ha='center', va='center',
                  size=10, xytext=(0, 8),
                  textcoords='offset points')
plt.xlabel('Mouse Button')
plt.ylabel('Number of Clicks')
plt.title('Mouse Clicks Per Button')
plt.show()

# Visualization: Mouse click coordinates heatmap
plt.figure(figsize=(10, 6))
sns.kdeplot(x=df_mouse_clicks['x'],
            y=df_mouse_clicks['y'], fill=True, cmap="coolwarm")
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Mouse Click Coordinates Heatmap')
plt.show()

# Visualization: Mouse paths
plt.figure(figsize=(10, 6))
plt.plot(df_mouse_paths['x'], df_mouse_paths['y'], 'b-', alpha=0.5)
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Mouse Paths')
plt.show()


plt.figure(figsize=(10, 6))
this = idle_time_per_hour.plot(kind='bar')
for bar in this.patches:
    this.annotate(format(bar.get_height(), '.2f'),
                  (bar.get_x() + bar.get_width() / 2,
                   bar.get_height()), ha='center', va='center',
                  size=10, xytext=(0, 8),
                  textcoords='offset points')
plt.xlabel('Hour of the Day')
plt.ylabel('Idle Time (seconds)')
plt.title('Idle Time Per Hour')
plt.show()


plt.figure(figsize=(10, 6))
this = scroll_events_per_direction.plot(kind='bar')
for bar in this.patches:
    this.annotate(format(bar.get_height(), '.2f'),
                  (bar.get_x() + bar.get_width() / 2,
                   bar.get_height()), ha='center', va='center',
                  size=10, xytext=(0, 8),
                  textcoords='offset points')
plt.xlabel('Scroll Direction')
plt.ylabel('Number of Scroll Events')
plt.title('Scroll Events Per Direction')
plt.show()


plt.figure(figsize=(10, 6))
this = scroll_events_per_hour.plot(kind='bar')
for bar in this.patches:
    this.annotate(format(bar.get_height(), '.2f'),
                  (bar.get_x() + bar.get_width() / 2,
                   bar.get_height()), ha='center', va='center',
                  size=10, xytext=(0, 8),
                  textcoords='offset points')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Scroll Events')
plt.title('Scroll Events Per Hour')
plt.show()


plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap="plasma_r", annot=True, fmt="f")
plt.xlabel('Hour of the Day')
plt.ylabel('Day of the Week')
plt.title('Key Presses Heatmap (Hour of Day vs. Day of Week)')
plt.show()


plt.figure(figsize=(10, 6))
email_volume.plot(kind='line')
plt.xlabel('Date')
plt.ylabel('Number of Emails')
plt.title('Email Volume Over Time')
plt.show()


plt.figure(figsize=(10, 6))
top_senders.plot(kind='bar')
plt.xlabel('Sender')
plt.ylabel('Number of Emails')
plt.title('Top 10 Senders')
plt.show()

# Visulization: Email Size Distribution (Scatter Plot)
plt.figure(figsize=(12, 8))
plt.semilogy(df_email['datetime'], df_email['size'],
             marker='o', markersize=2, alpha=0.5)
plt.xlabel('Time')
plt.ylabel('Email Size (bytes)')
plt.title('Email Size Distribution')
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
top_recipients.plot(kind='bar')
plt.xlabel('Recipient')
plt.ylabel('Number of Emails')
plt.title('Top 10 Recipients')
plt.show()


plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Email Subject Word Cloud')
plt.show()


plt.figure(figsize=(10, 6))
plt.hist(response_times, bins=50)
plt.xlabel('Response Time (minutes)')
plt.ylabel('Number of Emails')
plt.title('Email Response Times')
plt.show()


plt.figure(figsize=(10, 6))
sentiment_counts.plot(kind='bar')
plt.xlabel('Sentiment')
plt.ylabel('Number of Emails')
plt.title('Email Sentiment Analysis')
plt.show()


# plt.figure(figsize=(10, 6))
# df_email['date'] = df_email['datetime'].dt.date
# sns.lineplot(data=filtered_keyword_counts,
#              x='year_month', y='count', hue='keywords')
# plt.title('Trends of the Most Common Keywords in Email Bodies Over Time')
# plt.xlabel('Date')
# plt.ylabel('Keyword Frequency')
# plt.legend(title='Keywords')
# plt.show()
# plt.figure(figsize=(10, 6))
# keyword_trends.plot(kind='line')
# plt.xlabel('Date')
# plt.ylabel('Frequency')
# plt.title('Email Topics Over Time')
# plt.legend(keywords)
# plt.show()


plt.figure(figsize=(12, 8))
pos = nx.spring_layout(email_graph)
nx.draw(email_graph, pos, with_labels=True, node_size=50,
        node_color='skyblue', font_size=8, edge_color='gray')
plt.title('Email Interaction Network')
plt.show()

# Plot the trends of the top 10 keywords over time
plt.figure(figsize=(14, 7))
sns.lineplot(data=filtered_keyword_counts, x='date', y='count', hue='keywords')
plt.title('Trends of the Most Common Keywords in Email Bodies Over Time')
plt.xlabel('Date')
plt.ylabel('Keyword Frequency')
plt.legend(title='Keywords')
plt.show()

# plt.figure(figsize=(12, 8))
# plt.scatter(df_email['month_year'], df_email['hour'], alpha=0.5)
# plt.xlabel('Month-Year')
# plt.ylabel('Time of Day (Hour)')
# plt.xticks(rotation=90)
# plt.title('Emails by Time of Day (Scatter Plot)')
# plt.grid(True)
# plt.show()


plt.figure(figsize=(10, 6))
top_subjects.plot(kind='bar')
plt.xlabel('Email Subject')
plt.ylabel('Number of Emails')
plt.title('Most Common Email Subjects')
plt.show()
