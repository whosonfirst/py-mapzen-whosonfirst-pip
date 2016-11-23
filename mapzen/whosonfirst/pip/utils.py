import mapzen.whosonfirst.pip
import mapzen.whosonfirst.placetypes
import shapely.geometry
import logging

def reverse_geocoordinates(feature):

    props = feature['properties']
    
    lat = props.get('reversegeo:latitude', None)
    lon = props.get('reversegeo:longitude', None)
    
    if not lat or not lon:
        lat = props.get('lbl:latitude', None)
        lon = props.get('lbl:longitude', None)
    
    if not lat or not lon:
        lat = props.get('geom:latitude', None)
        lon = props.get('geom:longitude', None)
        
    if not lat or not lon:

        shp = shapely.geometry.asShape(feature['geometry'])
        coords = shp.centroid
        
        lat = coords.y
        lon = coords.x

    return lat, lon

# please rename me
# test with 18.48361, -77.53057

def whereami(feature, **kwargs):
    raise Exception, "Please finish me"

def append_hierarchy_and_parent_pip(feature, **kwargs):
    return append_hierarchy_and_parent(feature, **kwargs)

# https://github.com/whosonfirst/py-mapzen-whosonfirst-pip-utils/blob/f1ec12d3ffefd35768473aebb5e6d3d19e8d5172/mapzen/whosonfirst/pip/utils/__init__.py

def append_hierarchy_and_parent(feature, **kwargs):

    props = feature['properties']
    placetype = props['wof:placetype']

    lat, lon = reverse_geocoordinates(feature)
 
    # see also : https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server
    pip = mapzen.whosonfirst.pip.proxy()

    pt = mapzen.whosonfirst.placetypes.placetype(placetype)
    
    _hiers = []
    _rsp = []
    
    parents = pt.parents()

    logging.debug("feature is a %s, parents are %s" % (placetype, parents))

    for parent in parents:
        
        parent = str(parent)

        # TO DO: some kind of 'ping' to make sure the server is actually
        # there... (20151221/thisisaaronland)
        
        logging.debug("reverse geocode for %s w/ %s,%s" % (parent, lat, lon))

        try:
            rsp = pip.reverse_geocode(parent, lat, lon, exclude=["superseded", "deprecated"])
        except Exception, e:
            logging.debug("failed to reverse geocode %s @%s,%s" % (parent, lat, lon))
            continue

        if len(rsp):
            _rsp = rsp
            break

    wofid = props.get('wof:id', None)

    data_root = kwargs.get('data_root', '')
    
    for r in _rsp:
        
        id = r['Id']

        pf = mapzen.whosonfirst.utils.load(data_root, id)

        pp = pf['properties']
        ph = pp['wof:hierarchy']

        if len(ph) == 0:

            logging.warning("parent (%s) returned an empty hierarchy so making a truncated mock" % id)

            pt = pp['wof:placetype']
            pt = "%s_id" % pt
            ph = [ {pt: id} ]

        for h in ph:

            if wofid:
                h[ "%s_id" % placetype ] = wofid

            _hiers.append(h)

    parent_id = -1

    if len(_rsp) == 0:
        logging.debug("Failed to reverse geocode any parents for %s, %s" % (lat, lon))
    elif len(_rsp) > 1:  
        logging.debug("Multiple reverse geocoding possibilities %s, %s" % (lat, lon))
    else:
        parent_id = _rsp[0]['Id']

    props['wof:parent_id'] = parent_id
    
    props['wof:hierarchy'] = _hiers
    feature['properties'] = props

    return True
