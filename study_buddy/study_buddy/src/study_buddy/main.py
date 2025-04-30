#!/usr/bin/env python
import sys
import warnings

from study_buddy.crew import StudyBuddy

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'study_material_path': r"C:\Users\mevae\OneDrive\Documents\deepseek.pdf"
    }

    StudyBuddy().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'study_material_path': 'materials/Course1_ChainesDeMarkov_DiscreteTime.pdf'
    }
    
    try:
        StudyBuddy().crew().train(n_iterations=1, filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        StudyBuddy().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'study_material_path': r"C:\Users\mevae\OneDrive\Documents\deepseek.pdf"

    }
    
    try:
        StudyBuddy().crew().test(n_iterations=1, openai_model_name='openai/hf:meta-llama/Llama-3.1-405B-Instruct', inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
