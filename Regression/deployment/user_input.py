from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------
# Normalization Function
# ---------------------------

def normalize_text(value: str) -> str:
    """Remove extra spaces and convert text to title case."""
    return " ".join(value.strip().split()).title()


# ---------------------------
# Literal Types
# ---------------------------

TransmissionType = Literal[
    "Manual",
    "Automatic",
    "Semi-Auto",
    "Other"
]

FuelType = Literal[
    "Petrol",
    "Diesel",
    "Hybrid",
    "Electric",
    "Other"
]

CarMake = Literal[
    "Audi",
    "BMW",
    "Ford",
    "Hyundai",
    "Mercedes",
    "Skoda",
    "Toyota",
    "Vauxhall",
    "Volkswagen"
]


# ---------------------------
# User Input Schema
# ---------------------------

class UserInput(BaseModel):

    model: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=100,
            description="Model name of the car (e.g., Fiesta, A3, Polo, i20).",
            example="Fiesta"
        )
    ]

    year: Annotated[
        int,
        Field(
            ...,
            ge=1990,
            le=2030,
            description="Manufacturing year of the vehicle.",
            example=2018
        )
    ]

    transmission: Annotated[
        TransmissionType,
        Field(
            description="Transmission type of the vehicle.",
            example="Manual"
        )
    ]

    mileage: Annotated[
        float,
        Field(
            ...,
            ge=0,
            le=500000,
            description="Total distance travelled by the car in miles.",
            example=35000
        )
    ]

    fuelType: Annotated[
        FuelType,
        Field(
            description="Fuel used by the vehicle.",
            example="Petrol"
        )
    ]

    tax: Annotated[
        float,
        Field(
            ...,
            ge=0,
            le=1000,
            description="Annual road tax paid for the vehicle.",
            example=145
        )
    ]

    mpg: Annotated[
        float,
        Field(
            ...,
            gt=0,
            le=600,
            description="Fuel efficiency measured in Miles Per Gallon (MPG).",
            example=55.4
        )
    ]

    engineSize: Annotated[
        float,
        Field(
            ...,
            gt=0,
            le=10,
            description="Engine displacement in litres.",
            example=1.2
        )
    ]

    Make: Annotated[
        CarMake,
        Field(
            description="Manufacturer (brand) of the vehicle.",
            example="Ford"
        )
    ]

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str):
        return normalize_text(value)