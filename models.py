import peewee
import os

if os.environ.get('RUNNING_MODE'):
    RUNNING_MODE = os.environ.get('RUNNING_MODE')
else:
    RUNNING_MODE = input("What mode do you want to run models in (dev/prod): ")

assert RUNNING_MODE in ['dev', 'prod'], "Invalid value for running mode. Must be either of 'prod' or 'dev'."

if RUNNING_MODE == 'dev':
    database_name = 'test_database.db'
elif RUNNING_MODE == 'prod':
    database_name = 'database.db'

db = peewee.SqliteDatabase(database_name)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    nickname = peewee.CharField(max_length=100, null=True)
    chat_id = peewee.IntegerField(unique=True)


class Anime(BaseModel):
    users = peewee.ManyToManyField(User, backref='animes')  # A many to many field will be more efficient
    name = peewee.CharField(max_length=400, unique=True)
    episodes_url = peewee.TextField(null=True)
    last_episode = peewee.IntegerField(null=True)


if __name__ == '__main__':
    print("\nYou are about to create a database file called '{0}'. This may cause an " \
          "overwrite if it already exists".format(database_name))
    confirmation = input("Do you wish to proceed? (y/n): ")

    if confirmation.lower() == 'y':
        db.connect()
        db.create_tables([User, Anime, Anime.users.get_through_model()])
    elif confirmation.lower() == "n":
        print("Operation was cancelled.")
    else:
        print("Invalid response. Operation was cancelled either way")