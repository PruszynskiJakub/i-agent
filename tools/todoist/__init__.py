def get_dynamic_context() -> str:
    """Returns the list of available Todoist projects with an introduction."""
    return """Here is the current list of available projects in Todoist, represented in XML format:

""" + projects


def get_default_project_id() -> str:
    """Returns the ID of the default project in Todoist."""
    return "2334150459"


def get_project_name(id) -> str:
    """Returns the name of the project with the given ID."""
    if id == "2334150459":
        return "Inbox"
    elif id == "2345453677":
        return "iAgent"
    elif id == "2345454404":
        return "AI-augmented developer"
    elif id == "2345453739":
        return "Urgent & Important"
    elif id == "2345454316":
        return "Not Urgent & Important"
    elif id == "2345597838":
        return "Clients"
    else:
        return "Unknown"

projects = """
<projects>
    <project>
        <name>Inbox</name>
        <id>2334150459</id>
        <description>Default collection for incoming tasks and quick captures</description>
    </project>
    <project>
        <name>iAgent</name>
        <id>2345453677</id>
        <description>A project focused on creating a personal AI assistant in Python with Slack as frontend client</description>
    </project>
    <project>
        <name>AI-augmented developer</name>
        <id>2345454404</id>
        <description>Educational course creation for developers focusing on AI tools application and building AI-oriented mindset</description>
    </project>
    <project>
        <name>Urgent &amp; Important</name>
        <id>2345453739</id>
        <description>High-priority tasks requiring immediate attention</description>
    </project>
    <project>
        <name>Not Urgent &amp; Important</name>
        <id>2345454316</id>
        <description>Strategic and planning tasks for long-term goals</description>
    </project>
    <project>
        <name>Clients</name>
        <id>2345597838</id>
        <description>Client-related tasks and project management</description>
    </project>
</projects>
"""
