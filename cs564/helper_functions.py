import numpy as np
import datetime
import math
import sys
import random
import string

def calc_julian_date(tm):
    """ count of days since Jan 1 4713 BC for given day
    """
    dt = tm - datetime.datetime(2000, 1, 1, 12, 0)
    return (dt.days + (dt.seconds + dt.microseconds / (1000000.0)) / (24 * 3600.0) + 2451545)


def gen_decimals(num_nums, min_val, max_val, decimals=2):
    """ Generate list of random numbers between min_val and max_val with 
    up to given decimal significance
    """
    return [round(random.uniform(min_val, max_val), decimals) for i in range(num_nums)]


def generate_latlngs(lat_range, lon_range, num_pairs):
    """ generates list of tuples of latitude, longitude pairs
    """
    lats = gen_decimals(num_pairs, lat_range[0], lat_range[1], 3)
    lons = gen_decimals(num_pairs, lon_range[0], lon_range[1], 3)
    return zip(lats, lons)


def gen_strings(num_strings, size=10, chars=string.ascii_letters):
    """ returns list of randomly-generated strings of size 'size'. Lower and uppercase.
    """
    return [''.join(random.choice(chars) for x in range(size)) for i in range(num_strings)]


def generate_times(first, last, interval):
    """
    Generate list of times over which to iterate, based on given time interval
    Inputs:
        first (np.datetime64): datetime, in UTC, from which to begin stepping
        last (np.datetime64): datetime, in UTC, at which to end stepping
        interval (int): # of minutes between each iteration
    Returns:
        times (np.array([np.datetime64])): array of times
        num_times (int): number of times in array
    """
    increment = np.timedelta64(interval, 'm')
    times = np.arange(first, last, increment, dtype='datetime64')
    num_times = len(times)
    return times, num_times


def calc_sun_positions(lat, lon, times):
    """ Duffie & Beckman algorithm from Ed. 2 for finding sun pos.
    Based on latitude, time of year.
    INPUTS:
        lat (int): latitude of observer in decimal format
        lon (int): longitude of observer in decimal format
        times ([np.datetime64]): array of times over which to calculate vecs
    OUTPUTS:
        sun_angles ([[np.float]]): array of pairs of angles, azimuth and elevation
        sun_vecs ([[np.float]]): array of triplets for x, y, z of sun vectors
        times ([datetime])
    """
    num_times = len(times)
    # get array of times to iterate through
    jan1 = np.datetime64('2013-01-01T00:00Z')
    jan1_jday = calc_julian_date(jan1.astype(object))
    # store days of year as # day in year. e.g. Feb 1 is 32
    n = np.array(times - jan1, dtype='timedelta64[D]')
    n = np.array(n + 1, dtype='int')
    n_jdays = jan1_jday + n  # list of julian days for entire year

    d2r = math.pi / 180.0
    r2d = 180 / math.pi
    B = (n - 1) * 360 / 365.0

    # longitude input is -180<=lon<=180, so need to convert to deg west
    # where 0 is prime meridian
    L_loc = (360 - lon) if lon>= 0 else abs(lon)

    # standard meridian is closest longitude divisible by 15.
    lon_rem = L_loc % 15
    L_st = L_loc + (15 - lon_rem) if lon_rem >= 7.5 else L_loc - lon_rem

    delta = 23.45 * np.sin(d2r*360*(284+n)/365)
    omega_ew = np.arccos(np.tan(delta*d2r) / np.tan(lat * d2r))/d2r
    phai_delta = lat - delta
    E = ( 229.2 * (0.000075 + 0.001868 * np.cos(B*d2r) - 0.032077 * np.sin(B*d2r) - 
        0.014615 * np.cos(2*B*d2r) - 0.04089 * np.sin(2*B*d2r)) )
    dT = 4 * (L_st - L_loc) + E  # difference between solar time and std time
    dT_tdelta = np.array(dT, dtype='timedelta64[m]')
    solar_times = times + dT_tdelta

    hours = np.fromiter((tm.item().hour for tm in times), dtype=float)
    mins = np.fromiter((tm.item().minute for tm in times), dtype=float)
    omega = (hours + mins/60 + dT/60 - 12) * 15

    theta_z = np.arccos(np.cos(lat*d2r) * np.cos(delta*d2r) * np.cos(omega*d2r) + np.sin(lat*d2r)*np.sin(delta*d2r)) / d2r
    gamma_s2 = np.arcsin(np.sin(omega*d2r)*np.cos(delta*d2r) / np.sin(theta_z * d2r)) / d2r

    c1 = np.ones(len(omega))
    c2 = np.ones(len(omega))
    c3 = np.ones(len(omega))
    c1[abs(omega) > omega_ew] = -1
    c2[phai_delta < 0] = -1
    c3[omega<0] = -1

    sun_az = c1*c2*gamma_s2 + c3*(1-c1*c2) * 180/2 + 180
    sun_az[sun_az < 0] = 360 + sun_az[sun_az < 0]
    sun_alt = 90 - theta_z
    return sun_az, sun_alt

