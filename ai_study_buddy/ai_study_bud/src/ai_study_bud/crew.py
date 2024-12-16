from crewai import Agent, Crew, Process, Task , LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from langchain_community.llms import HuggingFaceHub


llm = LLM(
    api_key="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",
    model="huggingface/MBZUAI-Paris/Atlas-Chat-9B",
)
import os 
print('Exists', os.path.exists("materials/ML_classification.pdf"))

from crewai_tools import (
    FileReadTool,
    SerperDevTool,
	CodeInterpreterTool
)

file_tool = FileReadTool(file_path= "materials/ML_classification.pdf")
search_tool = SerperDevTool()
# Uncomment the following line to use an example of a custom tool
# from ai_study_bud.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class AiStudyBud():
	"""AiStudyBud crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def explaination_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['explaination_specialist'],
			verbose=True,
			tools=[file_tool , search_tool]
		)

	@agent
	def evaluation_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['evaluation_specialist'],
			verbose=True,
			tools=[file_tool]
		)
	@agent
	def flashcard_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['flashcard_creator'],
			tools=[file_tool ],
			verbose=True
		)
	@agent
	def summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['summarizer'],
			tools=[file_tool],
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['explanation_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['evaluation_specialist'],
			output_file='tests.json'
		)
	
	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['flashcard_creation_task'],
			output_file='card.json'
		)
	
	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['summary_creation_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AiStudyBud crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
