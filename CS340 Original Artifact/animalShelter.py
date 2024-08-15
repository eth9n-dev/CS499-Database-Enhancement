from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, usern, passw, hostn, portn, dbn, coln):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #
        # You must edit the connection variables below to reflect
        # your own instance of MongoDB!
        #
        # Connection Variables
        #
        USER = usern
        PASS = passw
        HOST = hostn
        PORT = portn
        DB = dbn
        COL = coln
        # HOST = 'nv-desktop-services.apporto.com'
        # PORT = 31874
        # DB = 'AAC'
        # COL = 'animals'
        #
        # Initialize Connection
        #
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]
        print("Successfully Connected")

# Complete this create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            self.database.animals.insert_one(data)  # data should be dictionary
            print("Successful creation")
            return True
        else:
            raise Exception("Nothing to save, because data parameter is empty")
            return False

# Create method to implement the R in CRUD.
    def read(self, data):
        if data is not None:
            cursor = self.database.animals.find(data)
            return cursor
        else:
            raise Exception("Data parameter is empty")
            return None
        
# Create update method to implement the U in CRUD.
    def update(self, query, value):
        if query and value is not None:
            x = self.database.animals.update_many(query, value)
            print(x.modified_count , "document(s) modified.")
            return x.modified_count
        else:
            raise Exception("Query/Values parameter is empty or invalid.")
            return 0
        
# Create delete method to implement the D in CRUD.
    def delete(self, query):
        if query is not None:
            x = self.database.animals.delete_many(query)
            print(x.deleted_count , "document(s) deleted.")
            return x.deleted_count
        else:
            raise Exception("Query parameter is empty or invalid.")
            return 0
            