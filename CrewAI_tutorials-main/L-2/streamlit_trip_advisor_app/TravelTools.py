import os
from crewai_tools import SerperDevTool

os.environ["SERPER_API_KEY"] = "1c09435b6cdee3f67714ce099da99140f2c9659e"

search_web_tool = SerperDevTool()
