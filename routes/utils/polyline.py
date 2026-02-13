from openrouteservice import convert


def decode_polyline(encoded):
    return convert.decode_polyline(encoded)["coordinates"]
