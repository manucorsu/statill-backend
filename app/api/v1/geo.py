from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from ..generic_tags import public
import app.geo as geo
from ...schemas.geo import GeocodeAddressResponse, ReverseGeocodingResponse

name = "geo"
router = APIRouter()


@router.get("/geocode", tags=public)
def geocode_address(
    address: str,
) -> GeocodeAddressResponse:
    """
    Geocode a given address string to retrieve geographic coordinates and formatted address.

    Args:
        address (str): The address string to be geocoded.

    Returns:
        GeocodeAddressResponse: A response object containing the geocoded address data,
                               including coordinates and formatted address information.
    """
    try:
        result = geo.geocode_address(address)
        return GeocodeAddressResponse(
            data=result,
            message=f"Successfully retrieved coordinates for address {result.formatted_address}.",
        )
    except (AssertionError, KeyError, ConnectionError) as ex:
        raise HTTPException(
            400,
            f"An error occurred on geocoding: ({type(ex)} {ex}). Please verify that your input is correct.",
        )


@router.get("/geocode/reverse", tags=public)
def reverse_geocode(
    latitude: float,
    longitude: float,
) -> ReverseGeocodingResponse:
    """
    Perform reverse geocoding to obtain address information from coordinates.

    Args:
        latitude (float): The latitude coordinate.
        longitude (float): The longitude coordinate.

    Returns:
        ReverseGeocodingResponse: A response object containing the geocoded address data
            and a formatted message with the provided coordinates.
    """
    try:
        result = geo.reverse_geocode(latitude, longitude)
        return ReverseGeocodingResponse(
            data=result,
            message=f"Successfully retrieved address for coordinates ({latitude}, {longitude}).",
        )
    except (AssertionError, KeyError, ConnectionError) as ex:
        raise HTTPException(
            400,
            f"An error occurred on reverse geocode: ({type(ex)} {ex}). Please verify that your input is correct.",
        )
