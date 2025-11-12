from pydantic import BaseModel
from .general import SuccessfulResponse


class CoordinatesAndFormattedAddress(BaseModel):
    latitude: float
    longitude: float
    formatted_address: str  # with format {street} {housenumber}, {suburb}, {district}, {postcode} {city}, {country}
    # eg. Venezuela 4100, Almagro, Comuna 5, 1202 Buenos Aires, Argentina


class Address(BaseModel):  # (formatted)
    address: str


class GeocodeAddressResponse(SuccessfulResponse):
    data: CoordinatesAndFormattedAddress
    message: str


class ReverseGeocodingResponse(SuccessfulResponse):
    data: Address
    message: str
