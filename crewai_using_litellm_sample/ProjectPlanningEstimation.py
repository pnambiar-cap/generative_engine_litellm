import os
import logging
import yaml
import litellm
from crewai import Agent, Task, Crew, LLM
from generative_engine_litellm.generative_engine_handler import GenerativeEngineLLM
#from helper import load_env
from typing import List
from pydantic import BaseModel, Field

# Configure logging
import logging

# Configure logging to capture debug information
# Explicitly configure the root logger to capture all logging levels and direct to both console and file
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicates
if logger.hasHandlers():
    logger.handlers.clear()

# Add handlers to both stream (console) and file
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("/tmp/crewai_debug_forced.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# Also set logging for third-party libraries explicitly
litellm_logger = logging.getLogger("litellm")
litellm_logger.setLevel(logging.INFO)
litellm_logger.addHandler(stream_handler)
litellm_logger.addHandler(file_handler)

crewai_logger = logging.getLogger("crewai")
crewai_logger.setLevel(logging.INFO)
crewai_logger.addHandler(stream_handler)
crewai_logger.addHandler(file_handler)

generative_engine_litellm = logging.getLogger("generative_engine_litellm")
generative_engine_litellm.setLevel(logging.INFO)
generative_engine_litellm.addHandler(stream_handler)
generative_engine_litellm.addHandler(file_handler)

# Configure logging to capture debug information for this script
logger.info("Logging is configured and started.")

# Step 1: Load environment variables
#load_env()

# Step 2: Load configuration path
config_path = os.path.join(os.getcwd(), '../generative_engine_config.yaml')
print(config_path)
# Load the custom LLM handler with the config path
generative_engine_llm = GenerativeEngineLLM(config_path=config_path)

# Register the custom handler with LiteLLM
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]

logger.info(f"Custom provider map: {litellm.custom_provider_map}")

# Step 3: Load agent and task configurations from YAML files
files = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

agents_config = configs['agents']
tasks_config = configs['tasks']

# Step 4: Define structured output models using Pydantic
class TaskEstimate(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")

class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")


print(litellm.custom_provider_map)
provider_list = [provider['provider'] for provider in litellm.custom_provider_map]
print(f"Available providers: {provider_list}")




# Step 5: Creating Agents using the custom LLM



# Creating Agents with more detailed debugging
try:
    logger.debug("Creating Project Planning Agent with config: %s", agents_config['project_planning_agent'])
    project_planning_agent = Agent(
        config=agents_config['project_planning_agent'],
        llm=LLM(model='generative-engine/openai.gpt-4o')
    )
    logger.info("Successfully created Project Planning Agent with model: %s", 'generative-engine/openai.gpt-4o')
except Exception as e:
    logger.error(f"Failed to create Project Planning Agent: {e}")

# Similarly for other agents
logger.debug("Creating Estimation Agent with config: %s", agents_config['estimation_agent'])
estimation_agent = Agent(
    config=agents_config['estimation_agent'],
    llm=LLM(model='generative-engine/openai.gpt-4o')
)
logger.info("Successfully created Estimation Agent with model: %s", 'generative-engine/openai.gpt-4o')

logger.debug("Creating Resource Allocation Agent with config: %s", agents_config['resource_allocation_agent'])
resource_allocation_agent = Agent(
    config=agents_config['resource_allocation_agent'],
    llm=LLM(model='generative-engine/openai.gpt-4o')
)
logger.info("Successfully created Resource Allocation Agent with model: %s", 'generative-engine/openai.gpt-4o')


# Step 6: Creating Tasks
task_breakdown = Task(
  config=tasks_config['task_breakdown'],
  agent=project_planning_agent
)

time_resource_estimation = Task(
  config=tasks_config['time_resource_estimation'],
  agent=estimation_agent
)

resource_allocation = Task(
  config=tasks_config['resource_allocation'],
  agent=resource_allocation_agent,
  output_pydantic=ProjectPlan  # This is the structured output we want
)

# Step 7: Creating Crew
crew = Crew(
  agents=[
    project_planning_agent,
    estimation_agent,
    resource_allocation_agent
  ],
  tasks=[
    task_breakdown,
    time_resource_estimation,
    resource_allocation
  ],
  verbose=True
)

#print("Available methods on Crew object:", dir(crew))

from rich.console import Console
from rich.markdown import Markdown

console = Console()

project = 'Website'
industry = 'Technology'
project_objectives = 'Create a website for a small business'
team_members = """
- John Doe (Project Manager)
- Jane Doe (Software Engineer)
- Bob Smith (Designer)
- Alice Johnson (QA Engineer)
- Tom Brown (QA Engineer)
"""
project_requirements = """
- Create a responsive design that works well on desktop and mobile devices
- Implement a modern, visually appealing user interface with a clean look
- Develop a user-friendly navigation system with intuitive menu structure
- Include an "About Us" page highlighting the company's history and values
- Design a "Services" page showcasing the business's offerings with descriptions
- Create a "Contact Us" page with a form and integrated map for communication
- Implement a blog section for sharing industry news and company updates
- Ensure fast loading times and optimize for search engines (SEO)
- Integrate social media links and sharing capabilities
- Include a testimonials section to showcase customer feedback and build trust
"""

# Format the dictionary as Markdown for a better display in Jupyter Lab
formatted_output = f"""
**Project Type:** {project}

**Project Objectives:** {project_objectives}

**Industry:** {industry}

**Team Members:**
{team_members}
**Project Requirements:**
{project_requirements}
"""
# Display the formatted output as Markdown
# Render the Markdown content in the terminal
console.print(Markdown(formatted_output))

# The given Python dictionary
inputs = {
  'project_type': project,
  'project_objectives': project_objectives,
  'industry': industry,
  'team_members': team_members,
  'project_requirements': project_requirements
}

# Step 8: Execute the crew tasks
if __name__ == "__main__":
    try:
        logger.info("Starting crew kickoff...")
        
        # Run the crew and capture the result
        result = crew.kickoff(inputs=inputs)
        
        # Log the result
        logger.info("Crew kickoff completed with result:")
        logger.info(result)

    except Exception as e:
        logger.error("Error occurred during crew execution: %s", e)