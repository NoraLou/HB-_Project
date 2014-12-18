
from flask import Flask, render_template, redirect, request, Response
import model
from sqlalchemy.orm import subqueryload
import json
import os

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get('some_secret')

 
@app.route("/")
def index():

    movements = model.session.query(model.Movement).all()

    for movement in  movements:
        d = {}
        print "*********************************"
        print movement.name
        if movement.numArtwork > 0:   
              for am in movement.artist_movements:
                  if am.artist.numImgs > 0:
                    possible_thumbnailURL = am.artist.artworks[0].thumbnailURL
                    # if the item isn't in our dictionary 
                    if d.get(possible_thumbnailURL, 0) == 0 :
                        d[possible_thumbnailURL] = d.get(possible_thumbnailURL, 1)
                        thumbnailURL = possible_thumbnailURL

        movement.thumbnailURL = thumbnailURL
        print movement.thumbnailURL
        print "*********************************"





    page = render_template("index.html")
    return page



@app.route("/api/movements", methods=['GET','POST'])
def load_movments():

    era = request.args.get('data')
    eras_movements = model.session.query(model.Movement).filter_by(era_id = era).all()
    json_movement_objs = [movement.convert_to_JSON()for movement in eras_movements]

    return Response(json.dumps(json_movement_objs), mimetype="text/json")



@app.route("/api/artists", methods= ['GET','POST'])
def load_artists():

    movement = request.args.get('data')

    movement_artists = model.session.query(model.Artist_movement).filter_by(movementId = movement).all()

    move_artists = []
    for artist in movement_artists: 
        name = artist.artist.name
        dates = artist.artist.dates
        numImgs = artist.artist.numImgs
        artistId = artist.artist.id
        thumbnailURL = artist.artist.thumbnailURL

        move_artists.append({"name":name,
            "id":artistId,
            "dates":dates,
            "numImgs": numImgs, 
            "thumbnailURL": thumbnailURL})
 
    return Response(json.dumps(move_artists), mimetype="text/json")


@app.route("/api/artwork", methods = ['GET','POST'])
def load_artwork():

    artist = request.args.get('data')

    artworks = model.session.query(model.Artwork).filter_by(artistId = artist).all()
    json_artwork_objs = [art.convert_to_JSON()for art in artworks] 

    return Response(json.dumps(json_artwork_objs), mimetype="text/json")



if __name__ == "__main__":
    app.run(debug = False)
    
