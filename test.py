import jwt

secret = '2ed154d0c89362da0e2fc49257c5fb27c01cdfbc85238ea334e84dbc8eccfee3812b41add4149999b2277780b0edbdda4905f46f607fd3ffd8d3601113c1e7ae'

token = jwt.encode({'HELLO': 'WHAT IS UP'}, secret, algorithm='HS512')

print(token)

result = jwt.decode(token, secret, algorithms=['HS512'])
print(result)

# from argon2 import PasswordHasher
# import sqlite3
# hasher = PasswordHasher()
# db = sqlite3.connect('data.db')
# cursor = db.cursor()
# cursor.executescript("""
# CREATE TABLE client (cid INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, client_secret TEXT);
# CREATE TABLE refresh_client_map (rid INTEGER PRIMARY KEY AUTOINCREMENT, refresh_token TEXT, expiry REAL, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid));
# CREATE TABLE action_client_map (aid INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, cid INTEGER, FOREIGN KEY(cid) REFERENCES client(cid));
# """
# )

# cursor = db.cursor()
# cursor.execute(
#     'INSERT INTO client (client_id, client_secret) VALUES (?, ?)',
#     ('test12312313', hasher.hash('test'))
# )
# db.commit()