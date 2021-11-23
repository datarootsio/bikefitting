"""
This file deploys the model as a REST API on Azure.
It returns information about the used resources as
well as the scoring url used trigger model inference.
"""
import os
from dotenv import load_dotenv
import time

import logging
from azureml.core import Environment, Workspace
from azureml.core.model import InferenceConfig, Model
from azureml.core.webservice import AciWebservice
from azureml.core.compute import ComputeTarget, AmlCompute, ComputeInstance
from azureml.exceptions import ComputeTargetException
from azureml.core.authentication import ServicePrincipalAuthentication

start = time.time()
logging.basicConfig(level=logging.INFO)
logging.getLogger("azure").setLevel(logging.ERROR)

load_dotenv()
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_ML_WORKSPACE_NAME = os.getenv("AZURE_ML_WORKSPACE_NAME")
AZURE_RESOURCEGROUP_NAME = os.getenv("AZURE_RESOURCEGROUP_NAME")

ws = Workspace.get(
    name=AZURE_ML_WORKSPACE_NAME,
    subscription_id=AZURE_SUBSCRIPTION_ID,
    resource_group=AZURE_RESOURCEGROUP_NAME,
    auth=ServicePrincipalAuthentication(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        service_principal_id=os.getenv("AZURE_CLIENT_ID"),
        service_principal_password=os.getenv("AZURE_CLIENT_SECRET"),
    ),
)

# Creating the Environment
env = Environment(name="movenet_thunder_environment")

requirements_path = os.path.join(
    os.path.dirname(__file__), "endpoint_env_requirements.txt"
)
with open(requirements_path, "r") as f:
    pip_packages = f.read()
    pip_packages = pip_packages.split("\n")

for package in pip_packages:
    env.python.conda_dependencies.add_pip_package(package)
env.inferencing_stack_version = "latest"

env.environment_variables = {
    "AZURE_STORAGE_CONNECTION_ACCOUNT": os.getenv("AZURE_STORAGE_CONNECTION_ACCOUNT"),
    "AZURE_CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
    "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
    "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
}

# Inference Config

src_dir_path = os.path.join(os.path.dirname(__file__), "..")
inference_config = InferenceConfig(
    environment=env, source_directory=src_dir_path, entry_script="entry.py"
)

# CREATE COMPUTE TARGET
compute_type = "COMPUTE_CLUSTER"
if compute_type == "COMPUTE_INSTANCE":
    deployment_target_name = "aci-inference"
elif compute_type == "COMPUTE_CLUSTER":
    deployment_target_name = "compcluster-inf"

try:
    if compute_type == "COMPUTE_INSTANCE":
        deployment_target = ComputeInstance(workspace=ws, name=deployment_target_name)
    elif compute_type == "COMPUTE_CLUSTER":
        deployment_target = ComputeTarget(workspace=ws, name=deployment_target_name)
    logging.info("Found existing deployment target")
except ComputeTargetException:
    logging.info("Creating a new deployment target...")
    vm_size = os.getenv("VM_SIZE")
    # GPU: Standard_NC6 (6 cores, 56 GB RAM, 1xNVIDIA Tesla K80) 1.17$/hr
    # CPU: Standard_F4s_v2 (4 cores, 8GB RAM) 0.19$/hr
    if compute_type == "COMPUTE_INSTANCE":
        prov_config = ComputeInstance.provisioning_configuration(vm_size=vm_size)
        deployment_target = ComputeInstance.create(
            workspace=ws,
            name=deployment_target_name,
            provisioning_configuration=prov_config,
        )
    elif compute_type == "COMPUTE_CLUSTER":
        prov_config = AmlCompute.provisioning_configuration(
            vm_size=vm_size,
            min_nodes=0,
            max_nodes=2,
            idle_seconds_before_scaledown=5 * 60,
        )
        deployment_target = ComputeTarget.create(
            workspace=ws,
            name=deployment_target_name,
            provisioning_configuration=prov_config,
        )
    deployment_target.wait_for_completion(show_output=True)

# Deployment Config
deployment_config = AciWebservice.deploy_configuration(
    cpu_cores=3.8,  # +0.2 default (max: 4 [West Europe])
    memory_gb=7,  # +1 default (max: 16 [West Europe])
    enable_app_insights=True,
    auth_enabled=False,
)

# DEPLOYMENT
service = Model.deploy(
    workspace=ws,
    name="movenetthunder",
    models=[],  # model is pulled from tensorflowhub
    inference_config=inference_config,
    deployment_config=deployment_config,
    deployment_target=deployment_target,
    overwrite=True,
    show_output=True,
)
service.wait_for_deployment(show_output=True)

logging.info("=" * 150)
logging.info(f"DEPLOYMENT COMPLETE - {time.time()-start:.0f}sec")
logging.info(f"WorkSpace: {ws}")
logging.info(f"Environment: {env}")
logging.info(f"Inference Config: {inference_config}")
logging.info(f"Deployment Config: {deployment_config}")
logging.info(f"Service: {service}")
logging.info(f"Model Endpoint scoring-url: {service.scoring_uri}")
logging.info(f"Model Endpoint swagger-url: {service.swagger_uri}")
logging.info("=" * 150)
