import requests
from requests.structures import CaseInsensitiveDict
from app.config import settings
from .schemas.geo import CoordinatesAndFormattedAddress, Address

__BIAS = "rect:-58.56423776348538,-34.716761557544764,-58.31633894381673,-34.50593425149832"  # rectángulo que agarra toda CABA y un poco del conurbano
PROVINCES = {
    "AR-A": "Provincia de Salta",
    "AR-B": "Provincia de Buenos Aires",
    "AR-C": "Ciudad Autónoma de Buenos Aires",
    "AR-D": "Provincia de San Luis",
    "AR-E": "Provincia de Entre Ríos",
    "AR-F": "Provincia de La Rioja",
    "AR-G": "Provincia de Santiago del Estero",
    "AR-H": "Provincia del Chaco",
    "AR-J": "Provincia de San Juan",
    "AR-K": "Provincia de Catamarca",
    "AR-L": "Provincia de La Pampa",
    "AR-M": "Provincia de Mendoza",
    "AR-N": "Provincia de Misiones",
    "AR-P": "Provincia de Formosa",
    "AR-Q": "Provincia del Neuquén",
    "AR-R": "Provincia de Río Negro",
    "AR-S": "Provincia de Santa Fe",
    "AR-T": "Provincia de Tucumán",
    "AR-U": "Provincia del Chubut",
    "AR-V": "Provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur",
    "AR-W": "Provincia de Corrientes",
    "AR-X": "Provincia de Córdoba",
    "AR-Y": "Provincia de Jujuy",
    "AR-Z": "Provincia de Santa Cruz"
}


def __format_address(geoapify_response):
    """
    Format a Geoapify geocoding response into a human-readable address string.

    Prioritizes Buenos Aires (CABA) as the top candidate when available, regardless
    of its position in the results list.

    Args:
        geoapify_response (Any): A dictionary containing geocoding results from Geoapify API.
            Must contain a "results" key with a list of location matches.

    Returns:
        tuple: A tuple containing:
            - str: Formatted address string with street, house number, suburb, district,
                   postcode, city, and country separated by commas.
            - dict: The selected candidate location dictionary.

    Raises:
        AssertionError: If geoapify_response is not a dict, results is not a list,
                       or no results are found.
        KeyError: (various), if the response is poorly formatted
    """
    assert isinstance(geoapify_response, dict), "Geoapify response must be a dictionary"

    results = geoapify_response["results"]
    assert isinstance(
        results, list
    ), "Geoapify response results must be a list of location matches"

    assert len(results) > 0, "No results found."
    candidate = results[0]
    assert isinstance(candidate,dict),"Geoapify response results must be a list of location matches"
    if (
        candidate["city"] != "Buenos Aires"
    ):  # siempre se prioriza CABA, aunque no sea la primera opc
        for c in results:
            if candidate["city"] == "Buenos Aires":
                candidate = c
    # Ensure mandatory fields are present
    mandatory_fields = ["street", "postcode", "city", "iso3166_2", "state", "country"]
    for field in mandatory_fields:
        assert field in candidate and candidate[field], f"Missing mandatory field: {field}"

    province = candidate["state"]
    try:
        province = PROVINCES[candidate["iso3166_2"]]
    except KeyError:pass

    # Build address with optional fields
    parts = [candidate["street"]]
    if candidate.get("housenumber"):
        parts[-1] += f" {candidate['housenumber']}"
    if candidate.get("suburb"):
        parts.append(candidate["suburb"])
    if candidate.get("district"):
        parts.append(candidate["district"])
    
    parts.append(f"{candidate['postcode']} {candidate['city']}")
    parts.append(province)
    parts.append(candidate["country"])
    
    formatted_address = ", ".join(parts)
    return (formatted_address, candidate)


def geocode_address(address: str) -> CoordinatesAndFormattedAddress:
    """
    Geocode an address string to retrieve its coordinates and formatted address.

    Uses the Geoapify API to convert a given address into latitude and longitude
    coordinates along with a standardized formatted address.

    Args:
        address (str): The address string to geocode. Must not be empty and should
                      be at least 5 characters long.

    Returns:
        CoordinatesAndFormattedAddress: An object containing the latitude, longitude,
                                       and formatted address of the geocoded location.

    Raises:
        AssertionError: If the address is empty or shorter than 5 characters.
        ConnectionError: If the Geoapify API request fails, including the status code
                        and error message returned by the API.
    """
    assert address.strip() != "", "Address cannot be empty."
    assert len(address) >= 5, "Address is too short to geocode."

    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&bias={__BIAS}&format=json&apiKey={settings.geoapify_api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    response = requests.get(url, timeout=10, headers=headers)
    jsonr = response.json()
    if response.status_code != 200:
        raise ConnectionError(
            f"Geocoding API request failed with status code {response.status_code} and message:\n{jsonr["error"]}\n{jsonr["message"]}"
        )

    formatted_address, candidate = __format_address(jsonr)
    return CoordinatesAndFormattedAddress(
        latitude=candidate["lat"],
        longitude=candidate["lon"],
        formatted_address=formatted_address,
    )


def reverse_geocode(latitude: float, longitude: float):
    url = f"https://api.geoapify.com/v1/geocode/reverse?lat={latitude}&lon={longitude}&format=json&apiKey={settings.geoapify_api_key}"
    print("\n\n\n", url)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    response = requests.get(url, headers=headers)
    jsonr = response.json()
    if response.status_code != 200:
        raise ConnectionError(
            f"Reverse geocoding API request failed with status code {response.status_code} and message:\n{jsonr["error"]}\n{jsonr["message"]}"
        )

    formatted_address, _ = __format_address(jsonr)

    return Address(address=formatted_address)
