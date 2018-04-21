import peewee


db = peewee.SqliteDatabase('database.db')


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
    db.connect()
    db.create_tables([User, Anime, Anime.users.get_through_model()])