[![maintained by dataroots](https://img.shields.io/badge/maintained%20by-dataroots-%2300b189)](https://dataroots.io)
 ![](https://media-exp1.licdn.com/dms/image/C4D1BAQFJFecNiY6xNA/company-background_10000/0/1606894615032?e=1628604000&v=beta&t=hNYzs9y3EA-620Ck8ip1QaZc77eXlH1ZUl-E-sLI6wo "Logo")
[![codecov](https://codecov.io/gh/datarootsio/bikefitting/branch/master/graph/badge.svg?token=7UPDN8GTYI)](https://codecov.io/gh/datarootsio/bikefitting)
[![Streamlit frontend](https://github.com/datarootsio/bikefitting/actions/workflows/frontend.yml/badge.svg)](https://github.com/datarootsio/bikefitting/actions/workflows/frontend.yml)
[![Azure Function](https://github.com/datarootsio/bikefitting/actions/workflows/function.yml/badge.svg)](https://github.com/datarootsio/bikefitting/actions/workflows/function.yml)
[![ML backend](https://github.com/datarootsio/bikefitting/actions/workflows/backend.yml/badge.svg)](https://github.com/datarootsio/bikefitting/actions/workflows/backend.yml)

<div id="top"></div>


[![LinkedIn][linkedin-shield]][linkedin-url]

![logo-dtr](https://user-images.githubusercontent.com/90327481/138892946-69b5f688-ff79-4b07-8864-44278b1695ca.png)

# rootsacademy-bikefitting
This is an easy-to-use tool to adjust your bike saddle to the ideal height based on a recommendation by a machine learning model.

## General
This is the graduation project of the rootsacademy of October 2021: A bikefitting application consisting of a website where users can upload a 10sec video of themselves on a bike trainer and receive a recommendation to either move the bike saddle up or down. To make the prediction a back-end script will estimate the position of hip, knee and heel for each frame of the video using [MoveNet](https://www.tensorflow.org/hub/tutorials/movenet). It then calculates the innerknee-angle and compares this angle to an optimal value of 145°. In case the angle is lower than 140°, the website will recommend the user to move the bike saddle up. In case the angle is higher than 150°, the website will recommend the user to move the bike saddle down. This repository contains the frontend and backend code of the project. This solution is supported on the cloud by Azure.

 More information on the project can be read in this [blog post](https://dataroots.io/rootlabs/contributions/next-generation-bike-fitting).

## Source:
We based our angle recommendations on the book: 'Bike fit' by Phil Burt.
(Burt, P. (2014). <i>Bike Fit, Optimise your bike position for high performance and injury avoidance</i>. London: Bloomsbury Publishing)
It is recommended in this book that the knee angle is between 140° and 150°. An angle around 140° would be more comfortable for the user
while an angle closer to 150° would be more performant.

## Built With

* [MoveNet](https://github.com/tensorflow/tfjs-models/tree/master/pose-detection/src/movenet)
* [Tensorflow](https://www.tensorflow.org/)
* [Azure](https://azure.microsoft.com)
* [Streamlit](https://streamlit.io/)
* [Terraform](https://www.terraform.io/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Quickstart

### Quickstart Deployment

- Clone the repository
- Follow the [terraform readme](terraform/README.md) instructions instantiate the github secrets and create the resources 
- Trigger the <a href="#workflow terraform">terraform workflow</a> to create the required resources on Azure
- Trigger the <a href="#workflow backend">backend</a>, <a href="#workflow frontend">frontend</a> and <a href="#workflow function">function</a> workflows to deploy the code to the newly created resources

### Quickstart Local Testing

- To test the solution locally, first create a virtual environment containing all dependencencies from the frontend/requirements.txt file. Within this virtual environment, from the rootdirectory, run


      streamlit run frontend/src/app.py


## Resources
A short section giving an overview of the resources used in this project.

Resources needed to deploy this application on Azure:
- 2 Resource groups
  - One for frontend and backend resources
  - One for Function resources
- Storage account
- Web app with service plan (frontend)
- Container registry with webhook
- Function app with service plan
  - [Function blob trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=python )
- Azure ML workspace (backend)
- Key vault

These resources can be created by using the Terraform scripts.

### Code
This repository contains all the code for this project.
### Deployment
Azure Cloud:
  - Data Storage: Azure Blob Storage
  - Website Hosting: Azure App Service
  - Backend Hosting: Azure ML

![Infrastructure](https://user-images.githubusercontent.com/90327481/140497408-1f5009d2-f3b4-4422-a8db-7621235192cb.png)

### GitHub Workflows
For deploying the different part of the solution there are four CI/CD piplines, with following jobs/steps. These workflows are automatically triggered when pushing to the master branch.
<div id="workflow frontend"></div>

1. Streamlit Frontend 
   - Check linting (black and flake8)
   - Run python test with coverage
   - Build and upload docker image for frontend to Azure Container Registry


<div id="workflow backend"></div>

2. ML Backend 
   - Check linting (black and flake8)
   - Run python test with coverage
   - Register and deploy backend model to Azure ML workspace and set model endpoint url in Azure Function
  
<div id="workflow function"></div>

3. Azure Function 
   - Check linting (black and flake8)
   - Deploy function code to Azure Function

<div id="workflow terraform"></div>

4. Terraform deployment
   - Terraform Init
   - Terraform Validate
   - Terraform Format check
   - Terraform Plan  
   - Terraform Apply

When using these pipelines make sure that the environment variables match with the resource names used. Also make sure that the Azure login details are stored in GitHub Secrets.


<p align="right">(<a href="#top">back to top</a>)</p>  

## Code Structure
<details>
   <summary> Tree Overview</summary>
   
   ```
   ├── backend
   │   ├── data
   │   │   └── videoinputquality_vs_angleaccuracy.csv
   │   ├── models
   │   │   ├── movenet_lightning
   │   │   │   └── ...
   │   │   └── movenet_thunder
   │   │       └── ...
   │   ├── notebooks
   │   │   └── ...
   │   ├── src
   │   │   ├── scripts
   │   │   │   └── ...
   │   │   ├── test
   │   │   │   └── ...
   │   │   ├── utils
   │   │   │   ├── azure.py
   │   │   │   ├── cropping.py
   │   │   │   ├── keypoints.py
   │   │   │   ├── model.py
   │   │   │   ├── postprocessing.py
   │   │   │   ├── preprocessing.py
   │   │   │   ├── utils.py
   │   │   │   └── visualizations.py
   │   │   ├── entry.py
   │   │   └── local_testing.py
   │   └── requirements.txt
   ├── frontend
   │   ├── images
   │   │   └── ...
   │   ├── src
   │   │   ├── scripts
   │   │   │   └── ...
   │   │   ├── test
   │   │   │   └── ...
   │   │   ├── utils
   │   │   │   ├── azure.py
   │   │   │   ├── datahandling.py
   │   │   │   ├── ui.py
   │   │   │   ├── utils.py
   │   │   │   └── visualizations.py
   │   │   ├── app.py
   │   ├── textfiles
   │   │   └── ...
   │   ├── config.toml
   │   ├── credentials.toml
   │   ├── Dockerfile
   │   └── requirements.txt
   ├── function
   │   ├── BlobTrigger
   │   │   ├── function.json
   │   │   └── __init__.py
   │   ├── host.json
   │   └── requirements.txt
   ├── terraform
   │   ├── images
   │   │   └── ...
   │   ├── backend.tf
   │   ├── frontend.tf
   │   ├── function.tf
   │   ├── main.tf
   │   ├── README.md
   │   └── variables.tf
   └── README.md
   ```
</details>


<!-- CONTACT -->
## Contact

- yannou@dataroots.io - Model
- chiel@dataroots.io - Web Service
- giliam@dataroots.io - Cloud
- liesbeth@dataroots.io - Deployment

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Special thanks to [MoveNet](https://github.com/tensorflow/tfjs-models/tree/master/pose-detection/src/movenet) for providing such a performant model and to our supervisors at dataroots for guiding us through this project.

<p align="right">(<a href="#top">back to top</a>)</p>


[linkedin-url]: https://www.linkedin.com/company/dataroots/mycompany/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
