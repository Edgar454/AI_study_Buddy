from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from src.study_buddy.tools.custom_tool import MaterialReadingTool , TavilyTool
from pydantic import BaseModel, Field
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['LITELLM_LOG'] = 'DEBUG'

GHLF_API_KEY = os.getenv("OPENAI_API_KEY")
GLHF_MAIN_MODEL_NAME = os.getenv("OPENAI_MAIN_MODEL_NAME")
GLHF_EXPLANATION_MODEL_NAME = os.getenv("OPENAI_EXPLANATION_MODEL")


from crewai_tools import (
    SerperDevTool,
	ScrapeWebsiteTool
)

material_reading_tool = MaterialReadingTool()
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
tavily_tool = TavilyTool()

# Pydantic output class
class Question(BaseModel):
    question: str = Field(..., description="The text of the question")
    options: List[str] = Field(..., description="List of answer options")
    answer: str = Field(..., description="The correct answer option (e.g., 'a', 'b')")


class EvaluationOutput(BaseModel):
    evaluation_dict: Dict[str, List[Question]] = Field(
        ..., description="The evaluation questions, categorized by difficulty level (e.g., Beginner, Intermediate, Advanced)"
    )

class Flashcard(BaseModel):
    section: str = Field(..., description="The section of the course or topic")
    recto: str = Field(..., description="The question or term shown on the front of the flashcard")
    verso: str = Field(..., description="The answer or explanation on the back of the flashcard")


class FlashcardsOutput(BaseModel):
    flashcard_dict: Dict[str, List[Flashcard]] = Field(
        ..., description="The flashcards categorized by difficulty level (e.g., Beginner, Intermediate, Advanced)"
    )


main_llm = LLM(
    model=GLHF_MAIN_MODEL_NAME,
    temperature=0.7
)

# LLM configuration
explanation_llm = LLM(
    model= GLHF_EXPLANATION_MODEL_NAME,
	temperature=0.4,
)



# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class StudyBuddy():
	"""StudyBuddy crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	
	@agent
	def ingestion_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['ingestion_agent'],
			verbose=True,
			tools=[material_reading_tool, search_tool , scrape_tool],
			llm= main_llm
            
		)

	@agent
	def explaination_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['explaination_specialist'],
			verbose=True,
			tools=[search_tool, scrape_tool,tavily_tool],
			llm = explanation_llm,
			max_iter = 5
		)

	@agent
	def evaluation_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['evaluation_specialist'],
			verbose=True,
			llm=main_llm,
		)
	
	@agent
	def flashcard_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['flashcard_creator'],
			verbose=True,
			llm=main_llm,
            
		)
	@agent
	def summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['summarizer'],
			verbose=True,
			llm=main_llm,
            
		)
	
	@task
	def ingestion_task(self) -> Task:
		return Task(
			config=self.tasks_config['ingestion_task'],

		)

	@task
	def explanation_task(self) -> Task:
		return Task(
			config=self.tasks_config['explanation_task'],
			context = [self.ingestion_task()]
		)

	@task
	def evaluation_task(self) -> Task:
		return Task(
			config=self.tasks_config['evaluation_task'],
			context = [self.ingestion_task() , self.explanation_task()],
			output_pydantic = EvaluationOutput ,
		)
	
	@task
	def flashcard_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['flashcard_creation_task'],
			context = [self.ingestion_task() , self.explanation_task()],
			output_pydantic = FlashcardsOutput ,
		)
	
	@task
	def summary_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['summary_creation_task'],
			context = [self.ingestion_task() , self.explanation_task()],
			output_file='outputs/summary.txt'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the StudyBuddy crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			language = 'fr'
		)
