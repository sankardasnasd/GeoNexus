# river.py

import requests
import math


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    lat1 = math.radians(
        float(lat1)
    )

    lon1 = math.radians(
        float(lon1)
    )

    lat2 = math.radians(
        float(lat2)
    )

    lon2 = math.radians(
        float(lon2)
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = (
        2
        *
        math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )

    return R * c


# ============================================================
# GET RIVERS NEAR LOCATION
# ============================================================

def get_rivers_near_location(
    lat,
    lon,
    radius=10000
):

    try:

        lat = float(lat)
        lon = float(lon)
        radius = int(radius)

    except (TypeError, ValueError):

        return {
            "error":
                "Invalid latitude, longitude or radius"
        }

    # ========================================================
    # OVERPASS SERVERS
    # ========================================================

    overpass_urls = [

        "https://overpass-api.de/api/interpreter",

        "https://overpass.kumi.systems/api/interpreter"

    ]

    # ========================================================
    # QUERY
    # ========================================================

    overpass_query = f"""
    [out:json][timeout:40];

    (
        way(
            around:{radius},
            {lat},
            {lon}
        )["waterway"="river"];

        way(
            around:{radius},
            {lat},
            {lon}
        )["waterway"="stream"];

        relation(
            around:{radius},
            {lat},
            {lon}
        )["waterway"="river"];
    );

    out tags center;
    """

    headers = {

        "User-Agent":
            "DisasterPredictionSystem/1.0"

    }

    data = None

    # ========================================================
    # REQUEST
    # ========================================================

    for overpass_url in overpass_urls:

        try:

            print(
                "\nTrying Overpass server:",
                overpass_url
            )

            response = requests.post(

                overpass_url,

                data={
                    "data":
                        overpass_query
                },

                headers=headers,

                timeout=45
            )

            response.raise_for_status()

            data = response.json()

            print(
                "River API successful"
            )

            break

        except requests.exceptions.RequestException as e:

            print(
                "River API request error:",
                str(e)
            )

            continue

        except ValueError as e:

            print(
                "River API JSON error:",
                str(e)
            )

            continue

    # ========================================================
    # NO DATA
    # ========================================================

    if data is None:

        return {
            "error":
                "Failed to fetch river data"
        }

    # ========================================================
    # PROCESS
    # ========================================================

    rivers = []

    for element in data.get(
        "elements",
        []
    ):

        tags = element.get(
            "tags",
            {}
        )

        name = tags.get(
            "name",
            "Unnamed river"
        )

        center = element.get(
            "center"
        )

        river_lat = None
        river_lon = None

        if center:

            river_lat = center.get(
                "lat"
            )

            river_lon = center.get(
                "lon"
            )

        # ====================================================
        # DISTANCE
        # ====================================================

        distance_km = None

        if (
            river_lat is not None
            and
            river_lon is not None
        ):

            distance_km = haversine(

                lat,
                lon,

                river_lat,
                river_lon
            )

        if distance_km is not None:

            rivers.append({

                "id":
                    element.get(
                        "id"
                    ),

                "type":
                    element.get(
                        "type",
                        "unknown"
                    ),

                "name":
                    name,

                "distance_km":
                    round(
                        distance_km,
                        3
                    ),

                "latitude":
                    river_lat,

                "longitude":
                    river_lon

            })

    # ========================================================
    # SORT
    # ========================================================

    rivers.sort(
        key=lambda x:
            x["distance_km"]
    )

    print(
        "\nRivers found:",
        len(rivers)
    )

    if rivers:

        print(
            "Nearest river:",
            rivers[0]
        )

    return rivers

# # import requests
# # import math


# # def haversine(lat1, lon1, lat2, lon2):
# #     # Radius of the Earth in kilometers
# #     R = 6371.0

# #     # Convert degrees to radians
# #     lat1_rad = math.radians(lat1)
# #     lon1_rad = math.radians(lon1)
# #     lat2_rad = math.radians(lat2)
# #     lon2_rad = math.radians(lon2)

# #     # Differences in coordinates
# #     dlat = lat2_rad - lat1_rad
# #     dlon = lon2_rad - lon1_rad

# #     # Haversine formula
# #     a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
# #     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# #     # Distance in kilometers
# #     distance = R * c
# #     return distance


# # def get_rivers_near_location(lat, lon, radius=10000):
# #     # Overpass API endpoint
# #     overpass_url = "http://overpass-api.de/api/interpreter"

# #     # Overpass QL query to find rivers within a radius (default 10km) of the given lat, lon
# #     overpass_query = f"""
# #     [out:json];
# #     (
# #       way(around:{radius}, {lat}, {lon})["natural"="water"]["water"="river"];
# #       relation(around:{radius}, {lat}, {lon})["natural"="water"]["water"="river"];
# #     );
# #     out body geom;
# #     """

# #     # Make the request to the Overpass API
# #     response = requests.get(overpass_url, params={'data': overpass_query})

# #     # Check if the response is successful
# #     if response.status_code == 200:
# #         data = response.json()

# #         # Extract the river details
# #         rivers = []
# #         for element in data.get("elements", []):
# #             river_info = {}
# #             # Check if the river has a 'name' tag
# #             if "tags" in element and "name" in element["tags"]:
# #                 river_info["name"] = element["tags"]["name"]
# #             else:
# #                 river_info["name"] = "Unnamed river"

# #             # Default distance as None to show that it wasn't calculated
# #             river_info["distance_km"] = None

# #             # Debugging: Print the raw geometry data for each element
# #             print("Element:", element)

# #             # Check if geometry exists and has valid lat/lon values
# #             if "geometry" in element and len(element["geometry"]) > 0:
# #                 lat_river = element["geometry"][0]["lat"]
# #                 lon_river = element["geometry"][0]["lon"]

# #                 # Calculate the distance if geometry exists
# #                 river_info["distance_km"] = haversine(lat, lon, lat_river, lon_river)
# #             else:
# #                 # In case geometry is missing, set distance as None and continue
# #                 river_info["distance_km"] = "Distance not available"

# #             # Store other river information
# #             river_info["id"] = element["id"]
# #             river_info["type"] = element.get("type", "unknown")
# #             rivers.append(river_info)

# #         return rivers
# #     else:
# #         return {'error': 'Failed to fetch river data'}

# import requests
# import math


# # ============================================================
# # HAVERSINE DISTANCE
# # ============================================================

# def haversine(
#     lat1,
#     lon1,
#     lat2,
#     lon2
# ):

#     R = 6371.0

#     lat1 = math.radians(float(lat1))
#     lon1 = math.radians(float(lon1))

#     lat2 = math.radians(float(lat2))
#     lon2 = math.radians(float(lon2))


#     dlat = lat2 - lat1
#     dlon = lon2 - lon1


#     a = (
#         math.sin(dlat / 2) ** 2
#         +
#         math.cos(lat1)
#         *
#         math.cos(lat2)
#         *
#         math.sin(dlon / 2) ** 2
#     )


#     c = 2 * math.atan2(
#         math.sqrt(a),
#         math.sqrt(1 - a)
#     )


#     return R * c


# # ============================================================
# # GET RIVERS
# # ============================================================

# def get_rivers_near_location(
#     lat,
#     lon,
#     radius=10000
# ):

#     try:

#         lat = float(lat)
#         lon = float(lon)
#         radius = int(radius)

#     except (TypeError, ValueError):

#         return {
#             "error": "Invalid latitude, longitude or radius"
#         }


#     # --------------------------------------------------------
#     # OVERPASS SERVERS
#     # --------------------------------------------------------

#     overpass_urls = [
#         "https://overpass-api.de/api/interpreter",
#         "https://overpass.kumi.systems/api/interpreter"
#     ]


#     # --------------------------------------------------------
#     # QUERY
#     # --------------------------------------------------------

#     overpass_query = f"""
#     [out:json][timeout:25];

#     (
#         way(
#             around:{radius},
#             {lat},
#             {lon}
#         )["waterway"="river"];

#         way(
#             around:{radius},
#             {lat},
#             {lon}
#         )["waterway"="stream"];

#         relation(
#             around:{radius},
#             {lat},
#             {lon}
#         )["waterway"="river"];
#     );

#     out tags center;
#     """


#     headers = {
#         "User-Agent":
#         "DisasterPredictionSystem/1.0"
#     }


#     # --------------------------------------------------------
#     # REQUEST
#     # --------------------------------------------------------

#     data = None


#     for overpass_url in overpass_urls:

#         try:

#             response = requests.post(
#                 overpass_url,
#                 data={
#                     "data": overpass_query
#                 },
#                 headers=headers,
#                 timeout=40
#             )


#             response.raise_for_status()


#             data = response.json()

#             break


#         except requests.RequestException as e:

#             print(
#                 "River API request error:",
#                 str(e)
#             )

#             continue


#         except ValueError as e:

#             print(
#                 "River API JSON error:",
#                 str(e)
#             )

#             continue


#     if data is None:

#         return {
#             "error": "Failed to fetch river data"
#         }


#     # --------------------------------------------------------
#     # PROCESS RIVERS
#     # --------------------------------------------------------

#     rivers = []


#     for element in data.get(
#         "elements",
#         []
#     ):

#         tags = element.get(
#             "tags",
#             {}
#         )


#         name = tags.get(
#             "name",
#             "Unnamed river"
#         )


#         river_lat = None
#         river_lon = None


#         # ----------------------------------------------------
#         # CENTER
#         # ----------------------------------------------------

#         center = element.get(
#             "center"
#         )


#         if center:

#             river_lat = center.get(
#                 "lat"
#             )

#             river_lon = center.get(
#                 "lon"
#             )


#         # ----------------------------------------------------
#         # DISTANCE
#         # ----------------------------------------------------

#         distance_km = None


#         if (
#             river_lat is not None
#             and
#             river_lon is not None
#         ):

#             distance_km = haversine(
#                 lat,
#                 lon,
#                 river_lat,
#                 river_lon
#             )


#         rivers.append({

#             "id":
#                 element.get(
#                     "id"
#                 ),

#             "type":
#                 element.get(
#                     "type",
#                     "unknown"
#                 ),

#             "name":
#                 name,

#             "distance_km":
#                 round(
#                     distance_km,
#                     3
#                 )
#                 if distance_km is not None
#                 else None,

#             "latitude":
#                 river_lat,

#             "longitude":
#                 river_lon
#         })


#     # --------------------------------------------------------
#     # SORT BY DISTANCE
#     # --------------------------------------------------------

#     rivers = [
#         r for r in rivers
#         if r["distance_km"] is not None
#     ]


#     rivers.sort(
#         key=lambda x: x["distance_km"]
#     )


#     return rivers