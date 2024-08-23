# LACE Index API
This project is an API developed in Python using Flask and Docker. The API calculates the LACE index either manually or automatically from an XLSX file. The LACE index is a predictive tool used to assess the risk of hospital readmission for patients.

# Table of Contents
* Installation
* Usage
* Endpoints
- Manual Index Calculation
- Automatic Index Calculation
* User Interface (Optional)
* Docker
* License

# Characteristics

* `Calculation of the LACE Index`: Determines the risk of hospital readmission based on patient admission and discharge data, number of emergency room visits, and type of admission.

* `Charlson Comorbidity Index Calculation`: Obtain the Charlson comorbidity index based on the patient's conditions.

* `REST API`: Support for HTTP requests using POST methods for file upload and manual calculation.

# Installation
`Clone the repository`:
* git clone https://github.com/juanjoramirez01/laceindex.git
* cd laceindex

# Install the dependencies
* pip install -r requirements.txt

# Usage
To run the API, execute the following command in your terminal:
* python lace.py

This will start a Flask development server. The server will run at http://127.0.0.1:5000 or http://192.168.1.93:5000 on your local network.


# Endpoints
Using the API with Postman

## Manual Index Calculation
To manually calculate the LACE index using Postman, follow these steps:

`Request Setup`
* HTTP Method: POST
* URL: http://127.0.0.1:5000/api/v1/manual_lace

`Request Body`
* Select the x-www-form-urlencoded option.

`Parameters`
* enfermedades: List of disease codes (e.g., I110,I517,I270,I48,I694,J90,F09,E110,N390).
* lengthStayDays: Number of hospital stay days (e.g., 2).
* admissionAcuity: Admission acuity level (1.NO, 2.YES).
* emergencyVisits: Number of emergency visits (e.g., 0).

`Expected Response`
json
{
    "Lace score": 10,
    "charlson_score": 7,
    "risk_level": "High risk of readmission"
}

## Automatic Index Calculation
`Request Setup`
* HTTP Method: POST
* URL: http://127.0.0.1:5000/api/v1/upload_lace

`Request Body`
* Select the form-data option
* Key: file

`Parameters`
* file: The XLSX file to upload.

`Expected Response`
json
[
    {
        "Charlson_Index": 0,
        "Fecha egreso": "2018-01-14",
        "Fecha ingreso": "2018-01-12",
        "LACE": 5,
        "LACE_Risk_Level": "Riesgo medio de readmision",
        "Num ingresos a urgencias en los ultimos 6 meses": 0,
        "Tipo de ingreso": "Urgente",
        "d1": "W188",
        "d15": null,
        "d2": "I10",
        "d3": "D728",
        "dp": "S328"
    },
    .
    .
    .
]

# User Interface (Optional)
This API includes an optional user interface that allows for quick use of the LACE index calculator without needing to interact directly with the API endpoints. To use the interface:

Run the API as usual (python lace.py).
Navigate to http://127.0.0.1:5000 in your web browser.
Use the provided forms to manually input data or upload an XLSX file to calculate the LACE index.
This interface is useful for testing or for those who prefer a graphical interface over sending HTTP requests.

# Docker
To build and run the application using Docker:

* Build the Docker image
docker build -t laceindex .
* Run the Docker container:
docker run -p 5000:5000 laceindex

This will start the API in a Docker container, and it will be accessible at http://127.0.0.1:5000.

# License
This project is licensed under the MIT License. See the LICENSE file for more information.
