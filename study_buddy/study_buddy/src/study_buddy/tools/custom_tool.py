from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.tools import TavilySearchResults
from PyPDF2 import PdfReader

class MyCustomTavilyToolInput(BaseModel):
    """Input schema for MyCustomTavilyTool."""
    query: str = Field(..., description="URL to search for.")

class TavilyTool(BaseTool):
    name: str = "Tavily Search Tool"
    description: str = "Search the web for a given query. Can also scrape and gather images ,\
        The results is a json file"
    args_schema: Type[BaseModel] = MyCustomTavilyToolInput

    def _run(self, query: str) -> str:
        tavily_tool = TavilySearchResults(
                                        max_results=5,
                                        include_answer=True,
                                        include_raw_content=True,
                                        include_images=True,
                                    )
        response = tavily_tool.invoke(query)
        return response



class StudyMaterialInput(BaseModel):
    """Input schema for MyCustomTool."""
    path: str = Field(..., description="the path to the study material that will be used for explanation")


class MaterialReadingTool(BaseTool):
    name: str = "PDF reading tool"
    description: str = (
        "This tool is designed to load and read the content of the study material"
    )
    args_schema: Type[BaseModel] = StudyMaterialInput

    def _run(self, path: str) -> str:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
