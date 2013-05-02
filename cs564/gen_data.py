import MySQLdb
import numpy as np
import sys
from helper_functions import *
import datetime
import random

""" TO WIPE OUT THE DB:
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE cs564_analysis;
DROP TABLE cs564_coordinate;
DROP TABLE cs564_analysiscomponent;
DROP TABLE cs564_observationpath;
DROP TABLE cs564_panel;
DROP TABLE cs564_pvarray;
DROP TABLE cs564_sunpath;
DROP TABLE cs564_sunposition;
SET FOREIGN_KEY_CHECKS=1;
"""

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + datetime.timedelta(seconds=random_second))



if __name__ == "__main__":

	# Quick note about logging:
    print """NOTE: the MySQLdb python interface does not display MySQL query information for successful queries.\nI manually add statements for successful queries.\nIf a query fails, the error/traceback is logged.\nOtherwise it usually just says "blah blah successful."
    \n\n"""
	

    # Set up connection to MySQL
    print "Connecting to MySQL database..."
    conn = MySQLdb.connect(
            host='us-cdbr-east-03.cleardb.com',
            user="b1196342b04fb6",
            passwd="da88a01a",
            db="heroku_17225a443718601"
            )
    # use a cursor to interact with the DB
    cur = conn.cursor()
    print "Connection established.\n"
    dt_now = datetime.datetime.now()
    start_date = datetime.datetime.strptime('4/30/2013 1:30 PM', '%m/%d/%Y %I:%M %p')
    #end_date = datetime.datetime.strptime('4/30/2013 11:30 PM', '%m/%d/%Y %I:%M %p')
    end_date = datetime.datetime.now()
    us_lat_range = (29.306, 46.529)
    us_lon_range = (-74.751, -123.706)


    empty_db = False
    ops_on = True
    panels_on = True
    arrays_on = True
    coords_on = True
    analyses_on = True
    components_on = True

    # prep db by clearing out previous data
    if empty_db:
        try:
            print "Clearing old data..."
            cur.execute("SET FOREIGN_KEY_CHECKS=0;")
            cur.execute("TRUNCATE TABLE cs564_AnalysisComponent")
            cur.execute("TRUNCATE TABLE cs564_Analysis")
            cur.execute("TRUNCATE TABLE cs564_Coordinate")
            cur.execute("TRUNCATE TABLE cs564_PVArray")
            cur.execute("DELETE FROM cs564_Panel")
            cur.execute("TRUNCATE TABLE cs564_SunPosition")
            cur.execute("DELETE FROM cs564_SunPath")
            cur.execute("TRUNCATE TABLE cs564_ObservationPath")
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")
            conn.commit()
            print "Truncation and deletion complete.\n"
        except:
            print sys.exc_info()
            conn.rollback()


    ########################
    # OBS PATHS: id, name (30 chars) and direction (0-360). Randomly generated.
    # we won't calc id - they'll be automatically entered and auto-incremented.
    ########################
    if ops_on:
        num_obs_paths = 1000
        obs_names = gen_strings(num_obs_paths)
        obs_directions = gen_decimals(num_obs_paths, 0, 360, decimals=2)
        random_dts = [random_date(start_date, end_date) for x in range(num_obs_paths)]
        #obs_paths = zip(obs_names, obs_directions, dt_nows)
        obs_paths = zip(obs_names, obs_directions, random_dts)
        try:
            print "Inserting 1000 Observation Path tuples..."
            cur.executemany(
                    """INSERT INTO cs564_ObservationPath (name, direction, created_at)
                    VALUES (%s, %s, %s)""",
                    obs_paths
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()



    ########################
    # PANELS
    ########################
    if panels_on: 
        num_panels = 1000
        names = gen_strings(num_panels)
        manufs = gen_strings(num_panels)
        descriptions = gen_strings(num_panels)
        reflectivity = gen_decimals(num_panels, 0, 1, decimals=3)
        refracs = gen_decimals(num_panels, 0, 5, decimals=5)
        random_dts = [random_date(start_date, end_date) for x in range(num_panels)]
        panel_list = zip(names, manufs, descriptions, reflectivity, refracs, random_dts)
        try:
            print "Inserting Panels tuples..."
            cur.executemany(
                    """INSERT INTO cs564_Panel(name, manufacturer, description, reflectivity, index_of_refrac, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    panel_list
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()



    ########################
    # PV Arrays
    ########################
    if arrays_on:
        num_arrays = 1000
        names = gen_strings(num_arrays)
        orients = gen_decimals(num_arrays, 0, 360, decimals=1)
        tilts = gen_decimals(num_arrays, 0, 90, decimals=1)
        heights = gen_decimals(num_arrays, 0, 1000, decimals=1)
        cur.execute("SELECT id from cs564_Panel")
        panel_ids = [item[0] for item in cur.fetchall()]
        random_dts = [random_date(start_date, end_date) for x in range(num_arrays)]
        panels = [random.choice(panel_ids) for x in range(num_arrays)]
        sun_paths = [None for i in range(num_arrays)]
        pv_arrays = zip(names, orients, tilts, heights, panels, sun_paths, random_dts)
        try:
            print "Inserting arrays..."
            cur.executemany(
                    """INSERT INTO cs564_PVArray (name, orientation, tilt, height, panel_id, sun_path_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    pv_arrays
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()



    # get pv_array ids, path ids
    cur.execute("SELECT id from cs564_PVArray")
    array_ids = [item[0] for item in cur.fetchall()]
    cur.execute("SELECT id from cs564_ObservationPath")
    op_ids = [item[0] for item in cur.fetchall()]

    ########################
    # PATH COORDINATES: lat, lon, elev, height, path or array
    ########################
    if coords_on:
        num_array_coords = 1000
        lat_lons = generate_latlngs([-90, 90], [-180, 180], num_array_coords)
        lats, lons = zip(*lat_lons)
        elevs = gen_decimals(num_array_coords, 0, 20000, 2)
        heights = gen_decimals(num_array_coords, 0, 1000, 2)
        #coord_paths = gen_decimals(num_array_coords, 0, num_obs_paths, 0)
        coord_arrays = [random.choice(array_ids) for x in range(num_array_coords)]
        coord_ops = [None for i in range(num_array_coords)]
        random_dts = [random_date(start_date, end_date) for x in range(num_array_coords)]
        coords = zip(lats, lons, elevs, heights, coord_ops, coord_arrays, random_dts)
        try:
            print "Inserting 2000 Coordinate tuples..."
            cur.executemany(
                    """INSERT INTO cs564_Coordinate (latitude, longitude, elevation,
                    height, path_id, pv_array_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    coords
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()

        num_op_coords = 1000
        lat_lons = generate_latlngs([-90, 90], [-180, 180], num_op_coords)
        lats, lons = zip(*lat_lons)
        elevs = gen_decimals(num_op_coords, 0, 20000, 2)
        heights = gen_decimals(num_op_coords, 0, 1000, 2)
        #coord_paths = gen_decimals(num_op_coords, 0, num_obs_paths, 0)
        coord_ops = [random.choice(op_ids) for x in range(num_array_coords)]
        coord_arrays = [None for i in range(num_op_coords)]
        random_dts = [random_date(start_date, end_date) for x in range(num_op_coords)]
        coords = zip(lats, lons, elevs, heights, coord_ops, coord_arrays, random_dts)
        try:
            print "Inserting 2000 Coordinate tuples..."
            cur.executemany(
                    """INSERT INTO cs564_Coordinate (latitude, longitude, elevation,
                    height, path_id, pv_array_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    coords
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()




    ########################
    # Analyses
    ########################
    if analyses_on:
        num_analyses = 1000
        names = gen_strings(num_analyses)
        descriptions = gen_strings(num_analyses)
        random_dts = [random_date(start_date, end_date) for x in range(num_analyses)]
        analyses = zip(names, descriptions, random_dts)
        try:
            print "Inserting analysis tuples..."
            cur.executemany(
                    """INSERT INTO cs564_Analysis (name, description, created_at)
                    VALUES (%s, %s, %s)""",
                    analyses
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()


    ########################
    # Analysis components
    ########################
    cur.execute("SELECT id from cs564_Analysis")
    analysis_ids = [item[0] for item in cur.fetchall()]
    if components_on:
        num_components = 500
        comp_analyses1 = [random.choice(analysis_ids) for x in range(num_components)]
        comp_analyses2 = [random.choice(analysis_ids) for x in range(num_components)]
        comp_empty = [None for x in range(num_components)]
        comp_paths = [random.choice(op_ids) for x in range(num_components)]
        comp_arrays = [random.choice(array_ids) for x in range(num_components)]
        random_dts1 = [random_date(start_date, end_date) for x in range(num_components)]
        random_dts2 = [random_date(start_date, end_date) for x in range(num_components)]
        components1 = zip(comp_analyses1, comp_paths, comp_empty, random_dts1)
        components2 = zip(comp_analyses2, comp_empty, comp_arrays, random_dts2)
        try:
            print "Inserting analysis tuples..."
            cur.executemany(
                    """INSERT INTO cs564_AnalysisComponent (analysis_id, path_id, pv_array_id, created_at)
                    VALUES (%s, %s, %s, %s)""",
                    components1
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()
        try:
            print "Inserting analysis tuples..."
            cur.executemany(
                    """INSERT INTO cs564_AnalysisComponent (analysis_id, path_id, pv_array_id, created_at)
                    VALUES (%s, %s, %s, %s)""",
                    components2
                    )
            conn.commit()
            print "Insertion successful.\n"
        except:
            print sys.exc_info()
            conn.rollback()



    print "Closing MySQL connection..."
    conn.close()
    print "Connection closed."
        
