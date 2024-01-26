from typing import Any

MAPPING: dict[str, dict[str, Any]] = {
    'uwind': {
        'code': 'UGRD', 
        'layer': '10 m above ground'
    },
    'vwind': {
        'code': 'VGRD',
        'layer': '10 m above ground'
    },
    'gust': {
        'code': 'GUST', 
        'layer': 'surface'
    },
    'tmin': {
        'code': 'TMIN', 
        'layer': '2 m above ground',
        'correction': -273,
        'unit_of_measure': '°C'
    },
    'tmax': {
        'code': 'TMAX', 
        'layer': '2 m above ground',
        'correction': -273,
        'unit_of_measure': '°C'
    },
    'tmp500hpa': {
        'code': 'TMP', 
        'layer': '500 mb',
        'correction': -273,
        'unit_of_measure': '°C'
    },
    'cldhigh': {
        'code': 'HCDC', 
        'layer': 'high cloud layer',
        'unit_of_measure': '%'
    },
    'cldmid': {
        'code': 'MCDC', 
        'layer': 'middle cloud layer',
        'unit_of_measure': '%'
    },
    'cldlow': {
        'code': 'LCDC', 
        'layer': 'low cloud layer',
        'unit_of_measure': '%'
    },
    'cldtotal': {
        'code': 'TCDC', 
        'layer': 'entire atmosphere',
        'unit_of_measure': '%'
    },
    'rain': {
        'code': 'APCP', 
        'layer': 'surface',
        'unit_of_measure': 'mm'
    },
    'cape': {
        'code': 'CAPE', 
        'layer': 'surface'
    },
    'liftedindex': {
        'code': '4LFTX',
        'layer': 'surface'
    },
    'pres': {
        'code': 'PRES', 
        'layer': 'surface',
        'unit_of_measure': 'hPa'
    },
    'vis': {
        'code': 'VIS', 
        'layer': 'surface',
        'unit_of_measure': 'm'
    }
}
