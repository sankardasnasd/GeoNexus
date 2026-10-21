# st.py

import time
import requests


# ============================================================
# SOIL API
# ============================================================

SOIL_API_URL = (
    "https://api.openepi.io/soil/type"
)


# ============================================================
# FETCH SOIL DATA
# ============================================================

def fetch_soil_data_with_retries(
    lat,
    lon,
    retries=3
):

    try:

        lat = float(lat)
        lon = float(lon)

    except (TypeError, ValueError):

        print(
            "Invalid latitude/longitude"
        )

        return None

    params = {

        "lat": lat,

        "lon": lon

    }

    for attempt in range(
        1,
        retries + 1
    ):

        try:

            print(
                "\n======================================"
            )

            print(
                "SOIL API REQUEST"
            )

            print(
                "======================================"
            )

            print(
                "Latitude :",
                lat
            )

            print(
                "Longitude:",
                lon
            )

            print(
                "URL:",
                SOIL_API_URL
            )

            response = requests.get(

                SOIL_API_URL,

                params=params,

                timeout=20
            )

            print(
                "Status Code:",
                response.status_code
            )

            print(
                "Response:",
                response.text[:1500]
            )

            response.raise_for_status()

            data = response.json()

            print(
                "\nFULL SOIL RESPONSE:"
            )

            print(
                data
            )

            if not isinstance(
                data,
                dict
            ):

                print(
                    "Invalid soil API response"
                )

                return None

            properties = data.get(
                "properties",
                {}
            )

            if not properties:

                print(
                    "No properties found."
                )

                return None

            soil_type = properties.get(
                "most_probable_soil_type"
            )

            if soil_type:

                print(
                    "Most probable soil type:",
                    soil_type
                )

                return data

            print(
                "most_probable_soil_type "
                "not found."
            )

            return None

        # ====================================================
        # TIMEOUT
        # ====================================================

        except requests.exceptions.Timeout:

            print(
                f"Soil API timeout "
                f"{attempt}/{retries}"
            )

            if attempt < retries:

                time.sleep(2)

        # ====================================================
        # HTTP ERROR
        # ====================================================

        except requests.exceptions.HTTPError as e:

            print(
                "Soil API HTTP error:",
                str(e)
            )

            try:

                print(
                    "Server response:",
                    response.text[:1000]
                )

            except Exception:
                pass

            # Don't retry 4xx errors

            if (
                response.status_code >= 400
                and
                response.status_code < 500
            ):

                break

            if attempt < retries:

                time.sleep(2)

        # ====================================================
        # REQUEST ERROR
        # ====================================================

        except requests.exceptions.RequestException as e:

            print(
                "Soil API request error:",
                str(e)
            )

            if attempt < retries:

                time.sleep(2)

        # ====================================================
        # JSON ERROR
        # ====================================================

        except ValueError as e:

            print(
                "Soil API JSON error:",
                str(e)
            )

            return None

        # ====================================================
        # OTHER ERROR
        # ====================================================

        except Exception as e:

            print(
                "Unexpected soil API error:",
                str(e)
            )

            if attempt < retries:

                time.sleep(2)

    print(
        "Unable to retrieve soil information."
    )

    return None




# # import time

# # import timeouts
# # from httpx import Client, Timeout, HTTPStatusError

# # # Replace with the desired latitude and longitude
# # latitude = 12.242538  # Example latitude (Change to your location)
# # longitude = 75.233321  # Example longitude (Change to your location)

# # # Set a higher timeout value (in seconds)
# # timeout = Timeout(10.0, read=15.0)  # Timeout for connection (10s) and read operation (15s)

# # # Retry mechanism with up to 3 retries
# # def fetch_soil_data_with_retries(lat, lon, retries=3):
# #     with Client(timeout=timeout) as client:
# #         for attempt in range(retries):
# #             try:
# #                 # Get the most probable soil type at the queried location
# #                 response = client.get(
# #                     url="https://api.openepi.io/soil/type",
# #                     params={"lat": lat, "lon": lon},
# #                 )

# #                 # Check for a successful response
# #                 response.raise_for_status()  # Raise error for bad responses (non-2xx status codes)

# #                 json = response.json()

# #                 # Check if the response contains the 'properties' field
# #                 if "properties" in json:
# #                     most_probable_soil_type = json["properties"].get("most_probable_soil_type", "No soil type found")
# #                     print(f"Most probable soil type: {most_probable_soil_type}")
# #                     return json  # Successful response
# #                 else:
# #                     print(f"Error: {json.get('error', 'Unknown error')}")
# #                     return None

# #             except HTTPStatusError as e:
# #                 print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
# #                 break  # Break the loop if a non-2xx response is returned
# #             except timeouts.ReadTimeout:
# #                 print(f"Attempt {attempt + 1}: Timeout occurred. Retrying...")
# #                 time.sleep(2)  # Wait before retrying
# #             except Exception as e:
# #                 print(f"An error occurred: {e}")
# #                 break  # Break the loop on any other error

# #         print("Max retries reached or error occurred.")
# #         return None  # If all retries fail

# # # Example usage

# import time

# from httpx import (
#     Client,
#     Timeout,
#     HTTPStatusError,
#     ReadTimeout
# )


# # ============================================================
# # HTTP TIMEOUT
# # ============================================================

# timeout = Timeout(
#     connect=10.0,
#     read=15.0,
#     write=15.0,
#     pool=15.0
# )


# # ============================================================
# # SOIL API
# # ============================================================

# def fetch_soil_data_with_retries(
#     lat,
#     lon,
#     retries=3
# ):

#     try:

#         lat = float(lat)
#         lon = float(lon)

#     except (TypeError, ValueError):

#         print("Invalid latitude/longitude for soil API")

#         return None


#     url = "https://api.openepi.io/soil/type"


#     for attempt in range(1, retries + 1):

#         try:

#             with Client(timeout=timeout) as client:

#                 response = client.get(
#                     url,
#                     params={
#                         "lat": lat,
#                         "lon": lon
#                     }
#                 )


#                 response.raise_for_status()


#                 data = response.json()


#                 properties = data.get(
#                     "properties"
#                 )


#                 if properties:

#                     soil_type = properties.get(
#                         "most_probable_soil_type"
#                     )

#                     print(
#                         "Most probable soil type:",
#                         soil_type
#                     )

#                     return data


#                 print(
#                     "Soil API response does not contain "
#                     "properties."
#                 )

#                 return None


#         except ReadTimeout:

#             print(
#                 f"Soil API timeout - "
#                 f"attempt {attempt}/{retries}"
#             )

#             if attempt < retries:
#                 time.sleep(2)


#         except HTTPStatusError as e:

#             print(
#                 "Soil API HTTP error:",
#                 e.response.status_code
#             )

#             print(
#                 "Response:",
#                 e.response.text[:500]
#             )

#             # Don't repeatedly retry 4xx errors
#             if 400 <= e.response.status_code < 500:
#                 break


#         except Exception as e:

#             print(
#                 f"Soil API error - "
#                 f"attempt {attempt}/{retries}:",
#                 str(e)
#             )

#             if attempt < retries:
#                 time.sleep(2)


#     print(
#         "Unable to retrieve soil information."
#     )

#     return None