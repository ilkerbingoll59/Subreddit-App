import praw
import mysql.connector
from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
username = os.environ.get("REDDIT_USERNAME")
password = os.environ.get("REDDIT_PASSWORD")

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="Redd App",
    username=username,
    password=password
)

db = mysql.connector.connect(
    host="mysql-server",
    user="root",
    password="deneme123",
    database="reddapp",
    port=3306
)

cursor = db.cursor()

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
if ("post",) not in tables:
    cursor.execute("CREATE TABLE post (title VARCHAR(255), author VARCHAR(255), score INT, permalink VARCHAR(255))")

@app.route("/")
def home():
    return {"message": "Bu web API, Reddit verilerini MySQL veritabanına kaydeder. /post/<subreddit_name> URL'i ile istediğiniz subreddit'in verilerini kaydedebilirsiniz."}

@app.route("/post/<subreddit_name>")
def redd_app(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    data = []
    for submission in subreddit.new(limit=10):
        title = submission.title
        author = submission.author.name if submission.author else "[Deleted]"
        score = submission.score
        permalink = submission.permalink

        query = "INSERT INTO post (title, author, score, permalink) VALUES (%s, %s, %s, %s)"
        values = (title, author, score, permalink)
        cursor.execute(query, values)
        db.commit()
        print(f"Kaydedildi: {title}-{author}")
        data.append({"title": title, "author": author, "score": score, "permalink": permalink})

    data = sorted(data, key=lambda x: x["score"], reverse=True)

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    cursor.close()
    db.close()
