import exifread
import math


def getLongLat(video):
    f = open(video, 'rb')
    longitude, longRef, latitude, latRef = extract_exif(f)
    if longitude == latitude == 0:
        return 0, 0

    if latRef == 'S': latitude = -latitude
    if longRef == 'W': longitude = -longitude
    latitude1 = float(latitude[0]) + float(latitude[1]) / 60 + float(latitude[2]) / 3600
    longitude1 = float(longitude[0]) + float(longitude[1]) / 60 + float(longitude[2]) / 3600
    return latitude1, longitude1


def extract_exif(file1):
    try:
        exif_tags = exifread.process_file(file1)
    except:
        return 0, 0, 0, 0

    if 'GPS GPSLongitude' in exif_tags:
        longitude = [x.num / x.den for x in exif_tags['GPS GPSLongitude'].values]
        latitude = [x.num / x.den for x in exif_tags['GPS GPSLatitude'].values]
        longRef = exif_tags['GPS GPSLongitudeRef'].values
        latRef = exif_tags['GPS GPSLatitudeRef'].values
        return longitude, longRef, latitude, latRef
    else:
        return 0, 0, 0, 0


def geographical_distance(lat1, lon1, lat2, lon2):
    R = 6372800

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def closest_location(lat, lon):
    locations = {
        "church": [52.012468, 4.360922],
        "stadhuis": [52.011548, 4.358495],
        "eemcs": [51.998895, 4.373478],
        "oudejan": [52.012707, 4.355859]
    }

    distances = {}

    for key, value in locations.items():
        distances[key] = geographical_distance(lat, lon, locations[key][0], locations[key][1])

    minimum = {k: v for k, v in sorted(distances.items(), key=lambda item: item[1])}

    return next(iter(minimum))
