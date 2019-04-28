import sqlite3
import os
def write_db():
    fnames = os.listdir()
    comments = []
    for fname in fnames:
        if 'thread' in fname:
            print(fname)
            with open(fname,'r') as f:
                x = f.readlines()
                i=0
                while i <  len(x) :
                    comments.append( (x[i][:-1],x[i+1][:-1],x[i+2][:-1],x[i+3][:-1],x[i+4][:-1]) )
                    i+=5
                f.close()

    print("total number of comments ", len(comments))


    connect = sqlite3.connect("db.sqlite3")
    con = connect.cursor()
    con.executemany("INSERT OR IGNORE into QQ(hash, ID, content, time, link) values (?,?,?,?,?)", comments)
    connect.commit()
    connect.close()


if __name__ == '__main__':
    write_db()
