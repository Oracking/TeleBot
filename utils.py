DB_TXT = 'db.txt'
CATEGORY_SEPARATOR = ' ||| '

def fetch_anime_db(db_txt=DB_TXT):
    separator = CATEGORY_SEPARATOR
    with open(db_txt, 'r') as db:
        lines = db.readlines()
        lines = [line.strip('\n').strip() for line in lines]
        anime_info = []
        for line in lines:
            name, last = tuple(line.split(separator))
            last = int(last)
            anime_info.append((name, last))
    return anime_info


def update_anime_db(new_data, db_txt=DB_TXT):
    separator = CATEGORY_SEPARATOR
    db = open(db_txt, 'r+')
    db.truncate(0)

    #Write data to database
    for index, data in enumerate(new_data):
        if index == len(new_data) -1:
            db.write('{0}{1}{2}'.format(data[0], separator, data[1]))
        else:
            db.write("{0}{1}{2}\n".format(data[0], separator, data[1]))

    db.close()


if __name__ == '__main__':
    results = fetch_anime_db('db.txt')
    print(results)

