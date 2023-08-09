
def add_client(client_name: str, note: str, type: str, auth: str, actions: list):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    #check if the client exists
    cursor.execute("SELECT cid FROM clients WHERE name = ?", (client_name,))
    row = cursor.fetchone()
    if(row):
        raise Exception('Client already exists.')
    

    client_id = str(uuid4())
    client_secret = str(uuid4())
    if(auth == 'access_token'):
        expiry = datetime.timestamp(datetime.now() + timedelta(days=360))
        access_token = jwt.encode({'cid': client_id, 'actions': actions, 'expiry': expiry, 'da': True}, client_secret, algorithm='HS256')
    cursor.execute(
        "INSERT INTO clients (cid, name, notes, type, auth, client_id, client_secret) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (client_id, client_name, note, type, auth, client_id, client_secret)
    )

    #add a client to the database
    pass

def remove_client(client_name: str):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("DELETE FROM clients WHERE name = ?", (client_name,))
    db.commit()
    #remove a client from the database
    pass

def get_clients(client_name: str|None = None):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    if client_name is None:
        cursor.execute("SELECT cid, name, notes FROM clients")
    else:
        name = '%' + client_name + '%'
        cursor.execute("SELECT cid, name, notes FROM clients WHERE name LIKE", (name,))
    
    return json.dumps(cursor.fetchall())

def get_action(cid):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM action_client_map WHERE cid = ?", (cid,))
    #return a list of functions that can be run
    pass

def add_action(cid: str, function_name: str):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("INSERT INTO action_client_map (cid, name) VALUES (?, ?)", (cid, function_name))
    db.commit()

def remove_action(cid, function_name: str):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("DELETE FROM action_client_map WHERE cid = ? AND name = ?", (cid, function_name))
    db.commit()
    
