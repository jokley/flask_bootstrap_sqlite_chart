import sqlite3
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/statistic')
def statistic():

    con = sqlite3.connect('database.db')
    #df = pd.read_sql_query("SELECT * from posts", con) 
    df = pd.read_sql_query("select date(created) as Datum ,count(*) as Anzahl, sum(count(*))over(order by date(created) asc)as Sum_Anzahl  from posts group by date(created)",con)
    labels = df['Datum'].values.tolist()
    values = df['Sum_Anzahl'].values.tolist()
    legend = 'Monthly Data'

   # labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
   # values = [5, 9, 8, 11, 6, 4, 7, 8]

    labels2 = df['Datum'].values.tolist()
    values21 = df['Anzahl'].values.tolist()
    values22 = df['Sum_Anzahl'].values.tolist()
    legend2 = 'Monthly Data'
   # labels2 = ["S", "M", "T", "W", "T", "F", "S"]
   # values21 =  [589, 445, 483, 503, 689, 692, 634]
   # values22 = [639, 465, 493, 478, 589, 632, 674]

    con.close()
    return render_template('statistic.html',values=values, labels=labels, legend=legend,values21=values21, values22=values22, labels2=labels2,legend2=legend2)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
