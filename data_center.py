"""
Satellite Brightness Calculator

Simple functions to calculate satellite brightness based on solar panel 
power requirements and viewing geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import lumos.conversions
import lumos.brdf.library
from lumos.brdf.library import BINOMIAL
from lumos.geometry import Surface
from starlink import satellitemodels
from analysis import calculator


# Constants
BASE_PANEL_AREA = 104.96  # m² per panel
BASE_POWER = 30.0  # kW per panel

# Default satellite model and earth BRDF
DEFAULT_SATELLITE_MODEL = satellitemodels.get_surfaces()
DEFAULT_EARTH_BRDF = lumos.brdf.library.PHONG(Kd=0.2, Ks=0.2, n=300)

def get_solar_array_brdf():
    """
    Get the BRDF model for solar arrays.
    
    Returns
    -------
    BINOMIAL
        Solar array BRDF model
    """
    # Solar array BRDF parameters
    B = np.array([[0.534, -20.409]])
    C = np.array([[-527.765, 1000., -676.579, 430.596, -175.806, 57.879]])
    lab_solar_array_brdf = BINOMIAL(B, C, d=3.0, l1=-3)
    
    return lab_solar_array_brdf  



def power_to_area(power_kw, continuous=False):
    """
    Convert power requirement to solar panel area.
    
    Parameters
    ----------
    power_kw : float
        Power requirement in kilowatts
    continuous : bool, optional
        If True, doubles the panel area for continuous power output.
        Default is False (instantaneous power).
    
    Returns
    -------
    float
        Solar panel area in square meters
    """
    # Calculate number of panels needed
    num_panels = power_kw / BASE_POWER
    
    # Calculate base area
    area = num_panels * BASE_PANEL_AREA
    
    # Double area if continuous power is required
    if continuous:
        area *= 2
    
    return area


def get_surfaces_with_solar_array(power_kw, continuous=False):
    """
    Get satellite surfaces including solar array for given power.
    
    Parameters
    ----------
    power_kw : float
        Power requirement in kilowatts
    continuous : bool, optional
        If True, uses continuous power configuration. Default is False.
    
    Returns
    -------
    list
        List of Surface objects
    """
    
    surfaces = DEFAULT_SATELLITE_MODEL.copy() 
    area = power_to_area(power_kw, continuous)
    solar_array_brdf = get_solar_array_brdf()
    solar_array_surface = Surface(area, [0, 1, 0], solar_array_brdf)
    surfaces.append(solar_array_surface)
    return surfaces


def calculate_brightness(sat_height, sat_altitude, sat_azimuth,
                         sun_altitude, sun_azimuth, power_kw, 
                         continuous=False, include_sun=True, 
                         include_earthshine=False, earth_panel_density=151, earth_brdf=None):
    """
    Calculate satellite brightness for given geometry and power.
    
    Parameters
    ----------
    sat_height : float
        Satellite height above ground in meters
    sat_altitude : float or array-like
        Satellite altitude angle(s) in degrees (0-90)
    sat_azimuth : float or array-like
        Satellite azimuth angle(s) in degrees (0-360)
    sun_altitude : float
        Sun altitude angle in degrees
    sun_azimuth : float
        Sun azimuth angle in degrees
    power_kw : float
        Solar panel power requirement in kilowatts
    continuous : bool, optional
        If True, uses continuous power configuration. Default is False.
    include_sun : bool, optional
        Include direct sunlight. Default is True.
    include_earthshine : bool, optional
        Include earthshine reflection. Default is False.
    earth_panel_density : int, optional
        Earth panel density for calculations. Default is 151.
    earth_brdf : object, optional
        Earth BRDF model. Default is PHONG(Kd=0.2, Ks=0.2, n=300)
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'intensity': Calculated intensity values
        - 'ab_magnitude': AB magnitude values
        - 'area': Solar panel area used (m²)
        - 'power_type': 'instantaneous' or 'continuous'
    """
    # Get surfaces with solar array
    surfaces = get_surfaces_with_solar_array(power_kw, continuous)
    
    # Set default earth BRDF if not provided
    if earth_brdf is None:
        earth_brdf = DEFAULT_EARTH_BRDF
    
    # Convert inputs to arrays if needed
    sat_altitude = np.atleast_1d(sat_altitude).astype(float)
    sat_azimuth = np.atleast_1d(sat_azimuth).astype(float)
    
    # Calculate intensity
    intensity = calculator.get_intensity_observer_frame(
        surfaces,
        np.ones(len(sat_altitude)) * sat_height,
        sat_altitude,
        sat_azimuth,
        sun_altitude,
        sun_azimuth,
        include_sun=include_sun,
        include_earthshine=include_earthshine,
        earth_panel_density=earth_panel_density,
        earth_brdf=earth_brdf
    )

    # Convert to AB magnitude
    ab_magnitude = lumos.conversions.intensity_to_ab_mag(intensity)
    
    return {
        'intensity': intensity,
        'ab_magnitude': ab_magnitude,
        'area': power_to_area(power_kw, continuous),
        'power_type': 'continuous' if continuous else 'instantaneous'
    }
