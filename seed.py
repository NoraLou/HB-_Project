import json
# from pprint import pprint
import model 
import csv
from model import session
import os


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def load_artists(session):
    f1 = unicode_csv_reader(open("artist_data.csv"), delimiter=",")
    # print dir(f1)
    f1.next()

    for row in f1:
        # print dir(row)
        artist = model.Artist() 
        artist.id = int(row[0])
        artist.name = row[1]
        artist.gender = row[2]
        artist.dates = row[3]
        artist.yearOfBirth = row[4]
        artist.yearOfDeath = row[5]
        artist.placeOfBirth = row[6]
        artist.info_url= row[7]

        session.add(artist)

    session.commit()



def load_artwork(session):
    f2 = unicode_csv_reader(open("artwork_data.csv"), delimiter = ",")
    f2.next()

    for row in f2:
        artwork = model.Artwork()
        artwork.artworkId = int(row[0])
        artwork.accession_number = row[1]
        artwork.artistRole = row[3]
        artwork.artistId = int(row[4])
        artwork.title = row[5]
        artwork.dateText = row[6]
        artwork.medium = row[7]
        artwork.creditLine = row[8]
        artwork.year = row[9]
        artwork.acquisitionYear = row[10]
        artwork.dimensions = row[11]
        artwork.width = row[12]
        artwork.height = row[13]
        artwork.depth = row[14]
        artwork.units = row[15]
        artwork.inscription = row[16]
        artwork.thumbnailCopyright = row[17]
        artwork.thumbnailURL = row[18]
        artwork.url = row[19]

        session.add(artwork)
    session.commit()


def load_json(file_name):
    file = open(file_name)
    json_text = file.read()
    file.close()

    data = json.loads(json_text)
    # pprint(data)

    artist_id = data.get("id")
    artist = model.session.query(model.Artist).filter_by(id = artist_id).first()

    # print "found artist", artist.name

    if data.get("movements",[]):
        print "found movements"
        print data["movements"]
        for movement in data["movements"]:
            print "found movement"
            print movement



            if movement.get("era"):
                print movement["era"]
              
                era_id = movement["era"].get("id")
                era_name = movement["era"].get("name")
                
                if era_id:
                    e = session.query(model.Era).get(era_id)
                    if not e:
                        e = model.Era()
                        e.id = era_id
                        e.name = era_name

                        session.add(e)


            movement_id = movement.get("id")
            movement_name = movement.get("name")

            if movement_id:
                print movement_id 
                print movement_name
            
                m = session.query(model.Movement).get(movement_id)
                if not m:
                    m = model.Movement()
                    m.id = movement_id
                    m.name = movement_name
                
                    session.add(m)

                else:
                    if m.name != movement_name:
                        print "ERROR!  movement name doesn't match!"
                        print movement_id, movement_name
                        print "database has: ", m.name

                am = model.Artist_movement()
                am.movementId = movement_id
                am.artistId = artist_id
                am.era_id = era_id

                session.add(am)


    session.commit()

def loop_Dir (file_path):
    for directr in os.listdir(file_path):
        print directr
        new_dir = file_path + "/" + directr
        print new_dir
        print os.listdir(new_dir)
        file_names = os.listdir(new_dir)
        for i in file_names:
            print i
            load_json(new_dir + "/" + i)

def add_details():
    movements = model.session.query(model.Movement).all()

    for movement in movements: 
        artistThumbnail = None
        numArtwork = 0
        for am in movement.artist_movements:
            if len(am.artist.artworks)>0:
            # if this movement has an artist with an artwork
                for artwork in range(len(am.artist.artworks)):
                    # for all the artworks assoc w/ movement
                    if am.artist.artworks[artwork].thumbnailURL: 
                        artistThumbnail = am.artist.artworks[artwork].thumbnailURL
                        numArtwork += len(am.artist.artworks)

        movement.thumbnailURL = artistThumbnail
        movement.numArtwork = numArtwork 
        movement.numArtist = len(movement.artist_movements)

        session.add(movement)

        eras = model.session.query(model.Era).all()

    for era in eras:
        moves_in_era = []
        numArtwork=0
        numArtist=0 
        print "*****************"
        print era.id
        print era.name
        movements_in_era = model.session.query(model.Artist_movement).filter(model.Artist_movement.era_id==era.id).group_by(model.Artist_movement.movementId).all()
        for artist_move in movements_in_era:
            moves_in_era.append([artist_move.movement.name])
            numArtist += artist_move.movement.numArtist
            numArtwork += artist_move.movement.numArtwork
        print moves_in_era
        print "numArtwork", numArtwork
        print "numArtist", numArtist












        

    session.commit()






def main():
    """In case we need this for something"""
    model.create_tables()
    load_artists(session)
    load_artwork(session)

    loop_Dir("./collection-master/artists")

    add_details()


if __name__ == "__main__":
    main()