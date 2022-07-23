from __future__ import annotations
from datetime import time
from typing import Any, NamedTuple, TypedDict


class WeatherResponseInfoType(TypedDict):
    _h: bool
    def_pressure_mm: int | float
    def_pressure_pa: int | float
    f: bool
    geoid: int | float
    lat: int | float
    lon: int | float
    n: bool
    nr: bool
    ns: bool
    nsr: bool
    p: bool
    slug: str
    tzinfo: dict[str, Any]
    url: str
    zoom: 10
    

class ForecastForHourType(TypedDict):
    cloudness: float
    condition: str
    feels_like: int | float
    hour: int
    hour_ts: int
    humidity: int | float
    icon: str
    is_thunder: bool
    prec_mm: int | float
    prec_period: int | float
    prec_prob: int | float
    prec_strength: int | float
    prec_type: int | float
    pressure_mm: int | float
    pressure_pa: int | float
    soil_moisture: int | float
    soil_temp: int | float
    temp: int | float
    uv_index: int
    wind_dir: str
    wind_gust: int | float
    wind_speed: int | float


class ForecastForPartType(TypedDict):
    _source: str
    cloudness: float
    condition: str
    daytime: str
    feels_like: int | float
    humidity: int | float
    icon: str
    polar: bool    
    prec_mm: int | float
    prec_period: int | float
    prec_prob: int | float
    prec_strength: int | float
    prec_type: int | float
    pressure_mm: int | float
    pressure_pa: int | float
    soil_moisture: int | float
    soil_temp: int | float
    temp_avg: int | float
    temp_max: int | float
    temp_min: int | float
    uv_index: int
    wind_dir: str
    wind_gust: int | float
    wind_speed: int | float

    
class DayForecastsType(TypedDict):
    biomet: dict[str, Any]
    date: str
    date_ts: int
    hours: list[ForecastForHourType]
    parts: dict[str, ForecastForPartType]
    moon_code: int
    moon_text: str
    rise_begin: str
    set_end: str
    sunrise: str
    sunset: str
    week: int


class WeatherResponseType(TypedDict):

    info: WeatherResponseInfoType
    fact: dict[str, Any]
    forecasts: list[DayForecastsType] 
    now: int
    now_dt: str
    yesterday: dict[str, Any]
    geo_object: dict[str, Any]
