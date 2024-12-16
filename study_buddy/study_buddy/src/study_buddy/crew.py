from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from study_buddy.tools.custom_tool import MaterialReadingTool , TavilyTool
from pydantic import BaseModel, Field


from crewai_tools import (
    SerperDevTool,
	ScrapeWebsiteTool
)

material_reading_tool = MaterialReadingTool()
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
tavily_tool = TavilyTool()

# Pydantic output class
class EvaluationOutput(BaseModel):
    evaluation_dict : dict = Field(..., description="The evaluation questions, containing questions sorted by level of difficulty")

class FlashcardsOutput(BaseModel):
    flascard_dict : dict = Field(..., description="flashcards organisées par niveau de difficulté, avec des questions et réponses précises")


# LLM configuration
llm = LLM(
    model="gemini/gemini-1.5-pro",
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
			tools=[material_reading_tool, search_tool , scrape_tool]
		)

	@agent
	def explaination_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['explaination_specialist'],
			verbose=True,
			tools=[search_tool, scrape_tool,tavily_tool],
			llm = llm
		)

	@agent
	def evaluation_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['evaluation_specialist'],
			verbose=True,
		)
	
	@agent
	def flashcard_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['flashcard_creator'],
			verbose=True
		)
	@agent
	def summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['summarizer'],
			verbose=True
		)
	
	@task
	def ingestion_task(self) -> Task:
		return Task(
			config=self.tasks_config['ingestion_task'],
			output_file='outputs/content.txt'

		)

	@task
	def explanation_task(self) -> Task:
		return Task(
			config=self.tasks_config['explanation_task'],
			output_file='outputs/explaination.txt',
			context = [self.ingestion_task()]
		)

	@task
	def evaluation_task(self) -> Task:
		return Task(
			config=self.tasks_config['evaluation_task'],
			context = [self.ingestion_task() , self.explanation_task()],
			output_pydantic = EvaluationOutput ,
			output_file='outputs/tests.json'
		)
	
	@task
	def flashcard_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['flashcard_creation_task'],
			context = [self.ingestion_task() , self.explanation_task()],
			output_pydantic = FlashcardsOutput ,
			output_file='outputs/card.json'
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
