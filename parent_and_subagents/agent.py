"""
Defines the agents for the first part of the lab (parent-subagent example).

This module contains the initial definitions for:
- 'attractions_planner': A sub-agent to list attractions for a country.
- 'travel_brainstormer': A sub-agent to help a user decide on a country.
- 'root_agent' ('steering'): The parent agent that directs the conversation
                            to the correct sub-agent.
"""
import os
import sys
import logging
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv, find_dotenv
import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from google.adk import Agent
from google.genai import types
from typing import Optional, List, Dict

from google.adk.tools.tool_context import ToolContext

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)
load_dotenv(find_dotenv(usecwd=True), override=False)

_ALLOWED_ADC_TYPES = {
    "authorized_user",
    "service_account",
    "external_account",
    "external_account_authorized_user",
    "impersonated_service_account",
    "gdch_service_account",
}

def ensure_valid_google_credentials():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        return
    if not os.path.isfile(creds_path):
        print(f"GOOGLE_APPLICATION_CREDENTIALS points to missing file: {creds_path}. Ignoring it.")
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        return
    try:
        with open(creds_path, "r", encoding="utf-8") as f:
            info = json.load(f)
        ctype = info.get("type")
        if ctype not in _ALLOWED_ADC_TYPES:
            print(
                "GOOGLE_APPLICATION_CREDENTIALS file has invalid type. "
                f"type={ctype!r}. Ignoring env var and falling back to ADC."
            )
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    except Exception as e:
        print(f"Failed to read GOOGLE_APPLICATION_CREDENTIALS file: {e}. Ignoring env var.")
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

ensure_valid_google_credentials()

def load_service_account_credentials():
    """Return service account credentials if GOOGLE_APPLICATION_CREDENTIALS points to a SA key."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        return None
    try:
        with open(creds_path, "r", encoding="utf-8") as f:
            info = json.load(f)
        if info.get("type") == "service_account":
            return service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
    except Exception as e:
        print(f"Failed to load service account credentials from file: {e}")
    return None

def get_cloud_logging_client():
    # Prefer explicit service account credentials when available
    sa_creds = load_service_account_credentials()
    if sa_creds:
        try:
            return google.cloud.logging.Client(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                credentials=sa_creds,
            )
        except Exception as e:
            print(f"Cloud logging with service account failed: {e}. Falling back to ADC.")
    try:
        return google.cloud.logging.Client()
    except DefaultCredentialsError:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        exists = bool(creds_path and os.path.isfile(creds_path))
        if creds_path:
            print(f"- GOOGLE_APPLICATION_CREDENTIALS={creds_path} (exists={exists})")
            if not exists:
                print("- File not found. Fix the path and retry.")
        else:
            print("- Set 'GOOGLE_APPLICATION_CREDENTIALS' to a service account JSON path or authenticate via 'gcloud auth application-default login'.")
        return None
    except Exception as e:
        print(f"Cloud logging init failed: {e}")
        return None

# Replace direct instantiation with helper
cloud_logging_client = get_cloud_logging_client()
if cloud_logging_client:
    cloud_logging_client.setup_logging()
else:
    logging.basicConfig(level=logging.INFO)

# Tools (add the tool here when instructed)


# Agents

attractions_planner = Agent(
    name="attractions_planner",
    model=os.getenv("MODEL"),
    description="Build a list of attractions to visit in a country.",
    instruction="""
        - Provide the user options for attractions to visit within their selected country.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # When instructed to do so, paste the tools parameter below this line

    )

travel_brainstormer = Agent(
    name="travel_brainstormer",
    model=os.getenv("MODEL"),
    description="Help a user decide what country to visit.",
    instruction="""
        Provide a few suggestions of popular countries for travelers.

        Help a user identify their primary goals of travel:
        adventure, leisure, learning, shopping, or viewing art

        Identify countries that would make great destinations
        based on their priorities.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

root_agent = Agent(
    name="steering",
    model=os.getenv("MODEL"),
    description="Start a user on a travel adventure.",
    instruction="""
        Ask the user if they know where they'd like to travel
        or if they need some help deciding.
        
        If they need help deciding, send them to 'travel_brainstormer'.
        If they know what country they'd like to visit, send them to the 'attractions_planner'.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    # Add the sub_agents parameter when instructed below this line
    sub_agents=[travel_brainstormer, attractions_planner]

)