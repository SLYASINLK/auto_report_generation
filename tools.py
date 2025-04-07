import requests
import psycopg2
from tavily import TavilyClient
from agents import function_tool
from datetime import datetime
from typing import List
import time

#################################################
# GET CURRENT DATE                              #
#################################################
@function_tool
async def get_current_date() -> str:
    """
    Get current date.
    """
    return datetime.now().strftime("%Y-%m-%d")

#################################################
# GEOCODE ADDRESS                              #
#################################################
@function_tool
async def geocode_address(address: str) -> dict:
    """
    Convert address to geographic coordinates (latitude and longitude) using Google Maps Geocoding API.

    Parameters:
    address (str): The address to be geocoded.

    Returns:
    dict: A dictionary containing geocoding results, including latitude and longitude.
    """
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': 'AIzaSyD2CNSJLAGhpfK7OxKXNdn0VHHMRlvRZxY'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        geocode_result = response.json()
        if geocode_result['results']:
            location = geocode_result['results'][0]['geometry']['location']
            return {'name': address, 'latitude': location['lat'], 'longitude': location['lng']}
        else:
            raise ValueError("Failed to get geocoding results for the address.")
    else:
        raise ConnectionError(f"Request failed, status code: {response.status_code}")
    
#################################################
# SEARCH COMPETITOR INFOMATION                  #
#################################################
@function_tool
async def search_competitor_infomation(
    latitude: float,
    longitude: float,
    radius: int,
    place_type: str,
    max_results: int
) -> List[dict]:
    """
    Search for nearby competitor businesses (e.g., restaurants, cafes) based on location and return detailed info.

    Parameters:
    - latitude: Latitude of the search center
    - longitude: Longitude of the search center
    - radius: Search radius in meters, e.g., 500
    - place_type: Type of competitor places to search, e.g., 'restaurant', 'cafe'
    - max_results: Maximum number of places to return, e.g., 5

    Returns:
    - A list of dictionaries, each representing a nearby competitor with:
      - name: Display name of the place
      - address: Formatted address of the place
      - rating: Google rating (if available)
      - priceLevel: Price level (1–4, if available)
      - openingHours: List of weekday opening hours (if available)
      - reviews: Up to 3 user reviews with author, text, and relative time
    """

    API_KEY = "AIzaSyD2CNSJLAGhpfK7OxKXNdn0VHHMRlvRZxY"

    # Step 1: Nearby search request
    nearby_url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": ",".join([
            "places.displayName",
            "places.location",
            "places.rating",
            "places.priceLevel",
            "places.regularOpeningHours",
            "places.formattedAddress",
            "places.id"
        ])
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius
            }
        }
    }

    nearby_response = requests.post(nearby_url, headers=headers, json=payload)
    if nearby_response.status_code != 200:
        return [{"error": f"Nearby search failed: {nearby_response.text}"}]

    places = nearby_response.json().get("places", [])
    results = []

    # Step 2: Get details for each place
    for place in places:
        place_id = place.get("id")
        if not place_id:
            continue

        detail_url = f"https://places.googleapis.com/v1/places/{place_id}"
        detail_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY
        }
        params = {
            "fields": ",".join([
                "displayName",
                "formattedAddress",
                "regularOpeningHours",
                "rating",
                "priceLevel",
                "reviews"
            ])
        }

        detail_response = requests.get(detail_url, headers=detail_headers, params=params)
        if detail_response.status_code != 200:
            continue

        data = detail_response.json()
        place_info = {
            "name": data.get("displayName", {}).get("text", "Unknown"),
            "address": data.get("formattedAddress", "No address"),
            "rating": data.get("rating", "No rating"),
            "priceLevel": data.get("priceLevel", "No price info"),
            "openingHours": data.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
            "reviews": [
                {
                    "author": r.get("authorDisplayName", "Anonymous"),
                    "text": r.get("text", {}).get("text", ""),
                    "time": r.get("relativePublishTimeDescription", "")
                }
                for r in data.get("reviews", [])[:3]  # Limit to top 3 reviews
            ]
        }
        results.append(place_info)
        time.sleep(0.3)  # Rate limit control

    return results

#################################################
# GET POSTGIS TABLE METADATA                     #
#################################################
@function_tool
async def get_postgis_table_metadata():
    """
    Get metadata for all tables in PostGIS database
    """
    import psycopg2
    from collections import defaultdict

    # Database connection configuration
    host = 'localhost'
    port = 5432
    dbname = 'site_selection'
    user = 'postgres'
    password = 'xzy565665'
    schema_filter = 'public'

    # Create connection
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cur = conn.cursor()

    # Query statement: exclude views, exclude specific tables, exclude gid column
    query = f"""
        SELECT 
            cols.table_name,
            cols.column_name,
            cols.udt_name
        FROM 
            information_schema.columns cols
        JOIN 
            information_schema.tables tabs 
        ON 
            cols.table_schema = tabs.table_schema AND cols.table_name = tabs.table_name
        WHERE 
            cols.table_schema = '{schema_filter}'
            AND tabs.table_type = 'BASE TABLE'
            AND cols.table_name NOT IN ('sg_pop', 'spatial_ref_sys')
            AND cols.column_name <> 'gid'
        ORDER BY 
            cols.table_name, cols.ordinal_position;
    """

    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Construct nested dictionary structure
    table_dict = defaultdict(list)

    for table_name, column_name, udt_name in rows:
        table_dict[table_name].append({
            "column": column_name,
            "data_type": udt_name
        })

    # Convert to list structure
    result = [
        {
            "table_name": table,
            "columns": columns
        }
        for table, columns in table_dict.items()
    ]

    return result

#################################################
# QUERY POSTGIS TEMPLATE                         #
#################################################
@function_tool
async def query_postgis_template(template: str) -> str:
    """
    Read SQL samples for querying PostGIS database
    - population_density: how to use coordinate to retrieve population density.
    - find_nearby_bus_stops: how to find nearby bus stops.
    - find_nearby_mrt_stations: how to find nearby mrt stations.
    """
    if template == "population_density":
        return '''
        SELECT 
        ST_Value(
            rast, 
            ST_SetSRID(ST_MakePoint(103.7766916, 1.2976493), 4326)
        ) AS pop_density
        FROM sg_pop
        WHERE 
        ST_Intersects(
            rast, 
            ST_SetSRID(ST_MakePoint(103.7766916, 1.2976493), 4326)
        );
        '''
    if template == "find_nearby_bus_stops":
        return '''
        SELECT * FROM find_nearby_bus_stops(103.7764, 1.2966);
        '''
    if template == "find_nearby_mrt_stations":
        return '''
        SELECT * FROM find_nearby_mrt_stations(103.7764, 1.2966, 3000);
        '''

#################################################
# QUERY POSTGIS DATABASE                        #
#################################################
@function_tool
async def query_postgis(sql_query: str) -> list:
    """
    Query PostGIS database with SQL and return results
    """
    connection = psycopg2.connect(
        dbname="site_selection",
        user="postgres",
        password="xzy565665",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    
    try:
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        connection.commit()
        return result
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        connection.close()

#################################################
# WEB SEARCH                                   #
#################################################
@function_tool
async def web_search(query: str) -> list[dict]:
    """
    Search the web using Tavily API and return results
    """
    client = TavilyClient("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")
    response = client.search(
        query=query,
        search_depth="advanced",
        include_answer="advanced"
    )
    extracted_data = [{"Title": item["title"], "Content": item["content"]} for item in response["results"]]
    return extracted_data