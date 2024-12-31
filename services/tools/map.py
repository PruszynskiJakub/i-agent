from dataclasses import dataclass
from services.tools.ynab import YnabService


@dataclass(frozen=True)
class ToolServices:
    ynab: YnabService


toolMap = {

}



def create_tool_services(
    repositories: Repositories
) -> ToolServices:
    return ToolServices(
        ynab=YnabService(repositories.ynab)
    )