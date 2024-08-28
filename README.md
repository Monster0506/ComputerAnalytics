# Personal Analytics Tool

## Overview

This Personal Analytics Tool is designed to capture and analyze various types of user interactions over extended periods. It collects data on keyboard and mouse activity, idle time, scrolling behavior, and email communications. The tool stores the collected data in an SQLite database and provides multiple visualization features to help you gain insights into your digital habits.

## Data Collected

### 1. **Keylogging Data**

- **Keystrokes**: Records every key pressed, along with a timestamp.
- **Key Hold Duration**: Measures the duration each key is held down.
- **Keypress Frequency**: Tracks the frequency of each keypress over time.

### 2. **Mouse Activity**

- **Mouse Clicks**: Captures the percentage of left, right, and middle clicks, along with the coordinates of each click.
- **Mouse Paths**: Records the paths taken by the mouse.
- **Mouse Scroll Events**: Logs scroll direction and timestamp.

### 3. **Idle Time**

- **Idle Time Tracking**: Measures periods of inactivity and records idle time data.

### 4. **Email Metadata**

- **Date and Time**: Captures the timestamp when an email is sent or received.
- **Subject**: Records the subject line of each email.
- **Sender and Recipient**: Stores the sender and recipient information.
- **Email Body**: Optionally records the content of the email.
- **Email Size**: Tracks the size of each email.

## Visualization Features

### Keylogging Visualizations

1. **Keystrokes per Hour**:

   - Visualizes the number of keystrokes recorded each hour of the day.

2. **Average Key Hold Duration**:

   - Displays the average duration for which each key is held down.

3. **Key Presses Heatmap**:

   - A heatmap showing key presses by the hour of the day and day of the week.

### Mouse Activity Visualizations

1. **Mouse Click Distribution**:

   - Shows the percentage distribution of mouse clicks by button type (left, right, middle).

2. **Mouse Click Heatmap**:

   - Visualizes the coordinates of mouse clicks on the screen.

3. **Mouse Path Visualization**:

   - Displays the paths taken by the mouse on the screen.

4. **Scroll Events Analysis**:

   - Analyzes scroll direction frequency and the amount of time spent scrolling.

### Idle Time Visualizations

1. **Idle Time Distribution**:
   - Visualizes idle time data over different hours of the day, helping to understand periods of inactivity.

### Email Metadata Visualizations

1. **Email Volume Over Time**:

   - A line graph showing the volume of emails sent/received over time.

2. **Top Senders and Recipients**:

   - Bar charts showing the top 10 senders and recipients of emails.

3. **Email Subject Word Cloud**:

   - Generates a word cloud from email subject lines to visualize common topics.

4. **Email Response Times**:

   - A histogram showing the distribution of response times for emails.

5. **Email Sentiment Analysis**:

   - Bar chart visualizing the sentiment (positive, neutral, negative) of email content.

6. **Email Topics Over Time**:

   - Line graph showing trends in email topics over time based on keyword analysis.

7. **Email Interaction Network**:

   - A network graph showing the interactions between senders and recipients.

8. **Email Length Distribution**:

   - Histogram showing the distribution of email lengths (number of characters).

9. **Emails by Time of Day**:

   - A scatter plot where the x-axis is the month across years and the y-axis is the time of day when emails were sent/received.

10. **Most Common Email Subjects**:

- Bar chart displaying the most frequently used email subjects.

1. **Email Size Distribution**:

- Scatter plot where the x-axis represents email index and the y-axis represents email size in bytes.

## Setup and Usage

1. **Database Setup**: The tool stores all data in an SQLite database. Ensure you have SQLite installed and configured.
2. **Running the Tool**: Execute the Python scripts provided to start collecting data. The tool is designed to run continuously in the background.
3. **Viewing Visualizations**: Use the visualization script to generate various charts and graphs based on the collected data. The visualizations are rendered using Matplotlib and Seaborn.

## Future Improvements

- **Customizable Dashboards**: Create a web-based dashboard for real-time data visualization.
- **Cross-Platform Compatibility**: Enhance support for multiple operating systems.
- **Data Export**: Add features to export data to CSV or other formats for further analysis.

## Disclaimer

This tool is intended for personal use only. Ensure you comply with all applicable laws and regulations when using keylogging or other data collection methods.

---
