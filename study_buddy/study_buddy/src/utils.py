from study_buddy.crew import StudyBuddy
from pathlib import Path

async def process_study_material(file_path: Path):
    """
    Process the study material and return the results.
    Replace this placeholder with the actual logic for processing the file.
    """
    try:
        inputs = {
            'study_material_path': file_path
        }
        results = await StudyBuddy().crew().kickoff_async(inputs=inputs)
        results = dict(results)
        tasks = ['explanation', 'evaluation', 'flashcard_building', 'summary']
        tasks_output = results['tasks_output'][1:]
        final_result = {task: task_output.raw for task, task_output in zip(tasks, tasks_output)}
        return final_result, results['token_usage']
    
    except Exception as e:
        raise RuntimeError(f"Error processing material: {str(e)}")