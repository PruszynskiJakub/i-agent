from uuid import uuid4

import requests

TOKEN = "xxx"


# Move an item
# Example move item request:
#
# $ curl https://api.todoist.com/sync/v9/sync \
#     -H "Authorization: Bearer 0123456789abcdef0123456789abcdef01234567" \
#     -d commands='[
#     {
#         "type": "item_move",
#         "uuid": "318d16a7-0c88-46e0-9eb5-cde6c72477c8",
#         "args": {
#             "id": "2995104339",
#             "parent_id": "2995104340"
#         }
#     }]'
# Example response:
#
# {
#   ...
#   "sync_status": {"318d16a7-0c88-46e0-9eb5-cde6c72477c8": "ok"},
#   ...
# }
# Move task to a different location. Only one of parent_id, section_id or project_id must be set.
#
# Command arguments
# Argument	Required	Description
# id
# String
# Yes	The ID of the task.
# parent_id
# String
# No	ID of the destination parent task. The task becomes the last child task of the parent task.
# section_id
# String
# No	ID of the destination section. The task becomes the last root task of the section.
# project_id
# String
# No	ID of the destination project. The task becomes the last root task of the project.
# Note, to move an item from a section to no section, just use the project_id parameter, with the project it currently belongs to as a value.

def move_task(task_id: str, project_id: str) -> bool:
    body = {
        "commands": [
            {
                "type": "item_move",
                "args": {"id": task_id, "project_id": project_id},
                "uuid": uuid4().hex,
            },
        ],
    }
    response = requests.post(
        "https://api.todoist.com/sync/v9/sync",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json=body,
    )
    return response.ok