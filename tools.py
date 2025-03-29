import requests
import psycopg2
from tavily import TavilyClient
from agents import function_tool
from datetime import datetime

@function_tool
async def get_current_date() -> str:
    """
    Get current date.
    """
    return datetime.now().strftime("%Y-%m-%d")

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

@function_tool
async def query_postgis_template(template: str) -> str:
    """
    Read SQL template for querying PostGIS database
    """
    if template == "population_density_indicator":
        return '''
        **population_density_indicator** caculation method:
        WITH all_poi_pop_values AS (
        SELECT ST_Value(r.rast, p.geom) AS pop_density
        FROM sg_poi p
        JOIN sg_pop r
        ON ST_Intersects(r.rast, p.geom)
        WHERE p.fclass = '{specific_category}' AND ST_Value(r.rast, p.geom) IS NOT NULL
        ),
        target_poi AS (
            SELECT ST_Value(r.rast, ST_SetSRID(ST_MakePoint({longtitude}, {latitude}), 4326)) AS target_density
            FROM sg_pop r
            WHERE ST_Intersects(r.rast, ST_SetSRID(ST_MakePoint({longtitude}, {latitude}), 4326))
        )
        SELECT 
            t.target_density,
            ROUND(100.0 * COUNT(a.pop_density) FILTER (WHERE a.pop_density <= t.target_density) / COUNT(a.pop_density), 2) AS percentile
        FROM all_poi_pop_values a, target_poi t
        GROUP BY t.target_density;
        '''

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