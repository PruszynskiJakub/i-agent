Title: Introduction to filters

URL Source: https://todoist.com/help/articles/introduction-to-filters-V98wIH

Markdown Content:
As Todoist starts to fill up with tasks, finding information needs to be speedy and efficient. That’s where filters come in handy! **Filters** are custom views for your tasks based on specific criteria. You can narrow down your lists according to task name, date, project, label, priority, date created, and more.

View the tasks in your filters in three different layouts: as a [list](https://todoist.com/help/articles/use-the-list-layout-in-todoist-AMAhHMVRH), a [board](https://todoist.com/help/articles/use-the-board-layout-in-todoist-AiAVsyEI), or a [calendar](https://todoist.com/help/articles/use-the-calendar-layout-in-todoist-lPHRQTu0o) (calendar layout is only available to Pro and Business customers)!

Create a filter
---------------

### Add a filter

1.  Select **Filters & Labels** in the sidebar.
2.  Click the **Add icon** next to Filters.
3.  In the **Add filter** window, enter the name of the filter or change the filter color. 
4.  Enter the filter query. Check out these [filter query examples](https://todoist.com/help/articles/introduction-to-filters-V98wIH#h_01J0J8ZDRBB65D2JTJ0RP0YCKB).
5.  Click **Add** to save your filter.
    
    💡 Optional: Click the toggle to add your filter to your [favorites](https://todoist.com/help/articles/add-a-project,-label,-or-filter-to-favorites-in-todoist-zezDfvSK) for easy access.
    

### Edit a filter

Click the **pencil icon** to the right of the filter name. Then, make changes to your filter.

### Use default filters

Give these default filters a try in Todoist:

*   **Assigned to me**: shows every task in Todoist assigned to you
*   **Priority 1**: shows all p1 tasks in Todoist
*   **View all**: shows all active tasks in Todoist

If you can't find the Filters & Labels view, it might be hidden from the sidebar. [Customize your sidebar](https://todoist.com/help/articles/customize-the-sidebar-in-todoist-S9JLTYqZV) and make sure it's set to appear with all your other views.

Break it down with symbols
--------------------------

There are a range of symbols you can use when creating filters in Todoist:

| Symbol | What it means | Example |
| --- | --- | --- |
| **|**
 | OR

 | _today | overdue_

 |
| &

 | AND

 | _today & p1_

 |
| !

 | NOT

 | _!subtask_

 |
| ()

 | Filter tasks based on queries inside parentheses first.

 | _(today | overdue) & #Work_

 |
| ,

 | Display filter queries in separate lists.

 | _date: yesterday, today_

 |
| \\

 | Use special characters in project, section, or label names as regular characters.

Filter tasks in projects, sections, or labels with two or more words in the name.

 | _#One \\& Two_

_#Shopping\\ list_

 |

Filter with advanced queries
----------------------------

Here’s a rundown of some of the more advanced filters you can use in Todoist:

### Filter based on:

In order to create filters based on keywords, you can use _search:_ followed by a keyword.

| If you need to | Use this |
| --- | --- |
| See all tasks that contain the word "Meeting"
 | _search: Meeting_

 |
| See all tasks that contain the word "Meeting" that are due today

 | _search: Meeting & today_

 |
| See all tasks that contain either the word "Meeting" or "Work"

 | _search: Meeting | search: Work_

 |
| See all tasks that contain the word "email"

 | _search: email_

 |
| See all tasks that contain web links

 | _search: http_

 |

Create a filter to either see or exclude sub-tasks in the view.

| If you need to | Use this |
| --- | --- |
| See all sub-tasks
 | _subtask_

 |
| See all parent tasks while excluding their sub-tasks

 | _!subtask_

 |

See all tasks scheduled for a specific date.

| If you need to | Use this |
| --- | --- |
| View all tasks scheduled for January 3rd
 | _date: Jan 3_

 |
| See all tasks dated before a specific date

 | _date before: May 5_ or _date before: 5/5_

 |
| See all tasks dated after a specific date

 | _date after: May 5_ or _date after: 5/5_

 |
| See all tasks scheduled within the next four hours and all overdue tasks

 | _date before: +4 hours_

 |
| See all tasks that are dated before the day you've selected in Settings \> General \> Next week

 | _date before: next week_

 |
| See all tasks dated in the current working week

 | _date before: sat_

 |
| See all tasks that are dated for next week

 | _(date: next week | date after: next week) & date before: 1 week after next week_

 |
| See all tasks dated within the current calendar month

 | _date before: first day_

 |
| See active tasks dated yesterday, along with today's tasks listed below

 | _date: yesterday, today_

 |
| See all tasks that have no date associated with them

 | _no date_

 |
| See all tasks with a date assigned to them

 | _!no date_

 |
| See all tasks with a date **and** time assigned to them

 | _!no date & !no time_

 |
| See all tasks dated today **and** before a specific time

 | _date: today & date before: today at 2pm_

 |
| See all tasks that are overdue

 | _Overdue_ or _over due_ or _od_

 |
| See all tasks that are overdue and have had time assigned to them, along with all tasks dated today and with time assigned to them

 | _overdue & !no time, date: today & !no time_

 |
| See all tasks in your Inbox without a date, followed by a separate section with all your tasks that have dates set, but are not in your Inbox

 | _#Inbox & no due date, All & !#Inbox & !no due date_

 |

You can write a date in any of these ways:

*   **Specific date**: 10/5/2022, Oct 5th 2022
*   **Specific date and time**: 10/5/2022 5pm, Oct 5th 5pm
*   **Relative date**: today, tomorrow, yesterday, 3 days (dated in the next 3 days), -3 days (dated in the past 3 days)
*   **Days of the week**: Monday, Tuesday, Sunday

| If you need to | Use this |
| --- | --- |
| See all tasks with no deadline
 | _no deadline_

 |
| See all tasks with a deadline

 | _!no deadline_

 |
| See all tasks with a deadline today

 | _deadline: today_

 |
| See all tasks with a deadline within the next 7 days

 | _deadline after: yesterday & deadline before: in 7 days_ |
| See all tasks with overdue deadlines

 | _deadline before: today_ |

Due takes into consideration the date and deadline fields. If a task has both, a date and deadline, due prioritizes the date. If the task does not have a date, due will check if the deadline matches filter criteria. If you don't use deadlines, due and date filters will return the same results.

| If you need to | Use this |
| --- | --- |
| View all tasks due on January 3rd
 | _Jan 3_

 |
| See all tasks that are due before a specific date

 | _due before: May 5_ or _due before: 5/5_

 |
| See all tasks that are due after a specific date

 | _due after: May 5_ or _due after: 5/5_

 |
| See all tasks due within the next four hours and all overdue tasks

 | _due before: +4 hours_

 |
| See all tasks that are due before the day you've selected in Settings \> General \> Next week

 | _due before: next week_

 |
| See all tasks due in the current working week

 | _due before: sat_

 |
| See all tasks that are due next week

 | _(due: next week | due after: next week) & due before: 1 week after next week_

 |
| See all tasks due within the current calendar month

 | _due before: first day_

 |
| See active tasks due yesterday, along with today's tasks listed below

 | _due: yesterday, today_

 |
| See all tasks that have no date or deadline associated with them

 | _no date_

 |
| See all tasks due today **and** before a specific due time

 | _today & due before: today at 2pm_

 |
| See all tasks that are overdue

 | _Overdue_ or _over due_ or _od_

 |
| See all tasks that are overdue and have had a specific time assigned to them, along with all tasks due today and with only assigned time

 | _overdue & !no time, today & !no time_

 |
| See all tasks in your Inbox without a date or deadline, followed by a separate section with all your tasks that are due, but are not in your Inbox

 | _#Inbox & no date, All & !#Inbox & !no date_

 |
| See all tasks due within the next 5 days

 | _5 days_ or _next 5 days_

 |
| See all tasks that have a recurring date

 | _recurring_

 |
| See all tasks that either have a non-recurring date or deadline, or no date at all assigned to them

 | _!recurring_

 |
| See all tasks with a date or deadline, but no due time, and which are not recurring

 | _no time & !recurring_

 |

| If you need to | Use this |
| --- | --- |
| See all tasks with priority level 1
 | _p1_

 |
| See all tasks with priority level 2

 | _p2_

 |
| See all tasks with priority level 3

 | _p3_

 |
| See all tasks with no priority level (i.e. p4)

 | _No priority_

 |

Create filters based on [labels](https://todoist.com/help/articles/introduction-to-labels-dSo2eE). For example, the filter `today & @email` will pull up all tasks with the `@email` label that are due today.

| If you need to | Use this |
| --- | --- |
| See all tasks with the label "email"
 | _@email_

 |
| See all tasks that don't have any labels

 | _no labels_

 |

| If you need to | Use this |
| --- | --- |
| See all tasks in the “Work” project
 | _#Work_

 |
| See all tasks in the "Work" project and its sub-projects

 | _##Work_

 |
| See all tasks in the "School" project and its sub-projects, but exclude the "Science" project

 | _##School & !#Science_

 |
| See all tasks belonging to sections named "Meetings" across all projects

 | _/Meetings_

 |
| See all tasks belonging to the section "Meetings" in the project "Work"

 | _#Work & /Meetings_

 |
| See all tasks not assigned to sections

 | _!/\*_

 |
| See all tasks not assigned to sections, but excluding tasks in your Inbox

 | _!/\* & !#Inbox_

 |

| If you need to | Use this |
| --- | --- |
| See all tasks in the “My Projects” workspace
 | _workspace: My projects_

 |
| See all tasks of the projects in the "Design team" folder

 | _##Design team_

 |
| Only see tasks in the "Doist" workspace

 | _workspace: Doist_

 |
| See all tasks in the "Doist" and "Halist" workspaces | (workspace: Doist | workspace: Halist) |

| If you need to | Use this |
| --- | --- |
| See all tasks created on a specific date
 | _created: Jan 3 2023_

 |
| See all tasks created more than 365 days ago

 | _created before: -365 days_

 |
| See all tasks created within the last 365 days

 | _created after: -365 days_

 |
| See all tasks created today

 | _created: today_

 |

When you search for tasks assigned to or by one of your collaborators, make sure that you use the name the collaborator uses in Todoist.

For example, Steve's real name might be Stephen Gray, but if he is listed as "Steve Gray" in Todoist, you should search _assigned by: Steve Gray_ or _assigned to: Steve Gray_.

**A collaborator can be identified by:**

*   The person’s email
*   The person’s full name
*   “Me” (referring to yourself)
*   “Others” (referring to all users other than yourself)

| If you need to | Use this |
| --- | --- |
| See all tasks that have been assigned to others
 | _assigned to: others_

 |
| See all tasks Steve Gray assigned

 | _assigned by: Steve Gray_

 |
| See all tasks that you assigned to others

 | _assigned by: me_

 |
| See all tasks that have been assigned to anyone (yourself and others)

 | _assigned_

 |
| See all tasks in shared projects

 | _shared_

 |
| See all tasks in your Todoist, excluding those assigned to others

 | _!assigned to: others_

 |

There aren't any filters for completed tasks because you can only filter for active tasks in Todoist. Instead, here's how to access and review your [completed tasks](https://todoist.com/help/articles/view-completed-tasks-in-todoist-J19h2s).

### Handy filters to try out

| If you need to | Use this |
| --- | --- |
| See all tasks that are overdue or due today that are in the “Work” project
 | _(today | overdue) & #Work_

 |
| See all tasks that don’t have a date

 | _no date_

 |
| See all tasks that don't have a time

 | _no time_

 |
| See all tasks that are due in the next 7 days and are labeled @waiting

 | _7 days & @waiting_

 |
| See all tasks created more than 365 days ago

 | _created before: -365 days_

 |
| See all tasks you assigned to others

 | _assigned by: me_

 |
| See all tasks assigned to Becky

 | _assigned to: Becky_

 |
| See all tasks created by you

 | _added by: me_

 |
| See all tasks created by Becky

 | _added by: Becky_

 |
| See all tasks in shared projects that haven’t been assigned to anyone

 | _shared & !assigned_

 |
| See all sub-tasks

 | _subtask_

 |
| See all parent tasks

Note

It's not possible to create a filter to display parent tasks with their sub-tasks.



 | _!subtask_

 |
| See all tasks

 | _view all_

 |
| See all uncompletable tasks

 | _uncompletable_

 |
| See all tasks due within the next 8 hours, but exclude all overdue tasks

 | _due before: +8 hours & !overdue_

 |
| See every unscheduled task in your #Work project

 | _#Work & no date_

 |
| See every high-priority task in the next two weeks

 | _(P1 | P2) & 14 days_

 |
| See tasks that were created more than 30 days ago

 | _created before: -30 days_

 |
| See all tasks with the label "night" that are scheduled for Saturday

 | _Saturday & @night_

 |
| See every task you’re assigned to in the project "Work"

 | _#Work & assigned to: me_

 |

Huge thanks to our Todoist ambassador, [Leighton Price](https://www.leightonprice.com/), for providing examples for this article.

Best practices for filters
--------------------------

As you get the hang of using filters, you’ll discover more ways to quickly surface information. Keep these best practices in mind to avoid bumping into errors:

### Combine filters with symbols

You can combine any filter query you want to get the exact view you need. Here are a few examples:

| If you need to | Use this |
| --- | --- |
| See all tasks that are due today and are also labeled @email
 | _Today & @email_

 |
| See all tasks that are labelled either @work or @office

 | _@work | @office_

 |
| See all tasks that are either due today or are overdue and are also in the “Work” project

 | _(today | overdue) & #Work_

 |
| See all tasks that are due in the next 7 days

 | _all & 7 days_

 |
| See all tasks that are not assigned to anyone

 | _!assigned_

 |
| See all tasks that are due today but exclude tasks in the "Work" project

 | _Today & !#Work_

 |
| See all tasks that are due tomorrow in the “Homework” project, but exclude tasks with the @languages label

 | _#Homework & tomorrow & !@languages_

 |

### Use a wildcard

To filter for tasks with similar symbols or characters, enter an asterisk (\*) in your search terms to use a wildcard.

For example, the filter query `@urgent*` will pull up a list of all tasks that have a label that start with the word “urgent”.

| If you need to | Use this |
| --- | --- |
| See all tasks with any label that starts with “home”. For example, @homework and @homeoffice
 | _@home\*_

 |
| See all tasks assigned to anyone whose first name starts with an M and last name is Smith

 | _assigned to: m\* smith_

 |
| See all tasks from projects which name ends with “work”. For example, #Artwork, #Network, and #Work

 | _#\*Work_

 |
| See all tasks from sections that have the word "Work" in the name. For example, /Work Meetings, /Work Admin, and /Work Calls

 | _Work\*_

 |
| See all tasks that don't belong to any section

 | _!/\*_

 |

If you need to search for a project which has an emoji in its title, you can use an asterisk to replace the emoji. For example, instead of adding `#Welcome 👋` to your query, you can add `#Welcome *`.

### Run two or more filter queries

You’ve the option to create multiple task lists in the same filter view by running several filter queries simultaneously. To separate each filter query in the view, add a comma ( , ).

For example, the filter query `p1 & overdue, p4 & today` shows two task lists in the same view:

*   A list of priority 1 overdue tasks
*   Priority 4 tasks that are due today

Use Filter Assist
-----------------

Filter Assist is currently only available in English and Spanish.

Let Filter Assist generate the right filter for you. Describe which tasks you'd like to see, and Filter Assist will do the rest:

1.  Click **Filters & Labels** in the sidebar.
2.  Click the **Add icon** next to Filters.
3.  Click **Try it** in the Filter Assist banner at the top.
4.  Describe which tasks you want to filter in the **Filter request** field.
5.  Click **Send**.
6.  Click **Add filter**.

Go further by customizing your filter. Change the filter's name, assign a different color, or add the filter to your favorites.

Delete a filter
---------------

1.  Click **Filters & Labels** in the sidebar.
2.  Right-click the filter or click the **three dots icon** beside the filter name.
3.  Select **Delete** to remove the filter.

Get started
-----------

Need some more ideas for filters? Try any of these handy [Todoist setups](https://app.todoist.com/app/templates/category/setups) to get started. If you’re having trouble creating or using filters in Todoist, [get in touch with us](https://todoist.com/help/articles/contact-todoist-for-help-PcZc394Kj). We—Marco, Dermot, Summer, or any of our other teammates—are more than happy to help!

FAQ
---

The order in which tasks are [sorted in a filter](https://todoist.com/help/articles/default-sorting-order-for-todoist-tasks-mqmgerY7) depends on whether it includes date queries:

*   When using a filter _with_ date queries: time → priority → task creation date and time → project ID → task ID
*   When using a filter _without_ date queries: priority → time and date → project order → task order within their project

If you want to only view tasks that are either assigned to you or unassigned, and exclude tasks assigned to others, you can use this query: _!assigned to: others_.

For example, if you wanted to see tasks with the label @work that are not assigned to other people, use: _@work & !assigned to: others_.

If you only want to see tasks that are assigned to you (excluding unassigned tasks), this filter will help: _assigned to: me_.

For example, if you wanted to see tasks with priority 1 that are assigned to you, use: _p1 & assigned to: me_.

