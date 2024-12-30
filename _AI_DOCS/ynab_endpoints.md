Title: YNAB API Endpoints - v1

URL Source: https://api.ynab.com/v1

Markdown Content:
YNAB API Endpoints - v1
===============  

![Image 2: Swagger UI](blob:https://api.ynab.com/0f46134dad4fe9bf36aba13c4eadbc9d)

Explore

YNAB API Endpoints 1.72.1 

OAS 3.0
-----------------------------------

[/papi/open\_api\_spec.yaml](https://api.ynab.com/papi/open_api_spec.yaml)

Our API uses a REST based design, leverages the JSON data format, and relies upon HTTPS for transport. We respond with meaningful HTTP response codes and if an error occurs, we include error details in the response body. API Documentation is at https://api.ynab.com

Servers

Authorize

### [User](https://api.ynab.com/v1#/User)

GET[/user](https://api.ynab.com/v1#/User/getUser)

User info

### [Budgets](https://api.ynab.com/v1#/Budgets)

GET[/budgets](https://api.ynab.com/v1#/Budgets/getBudgets)

List budgets

GET[/budgets/{budget\_id}](https://api.ynab.com/v1#/Budgets/getBudgetById)

Single budget

GET[/budgets/{budget\_id}/settings](https://api.ynab.com/v1#/Budgets/getBudgetSettingsById)

Budget Settings

### [Accounts](https://api.ynab.com/v1#/Accounts)

The accounts for a budget

GET[/budgets/{budget\_id}/accounts](https://api.ynab.com/v1#/Accounts/getAccounts)

Account list

POST[/budgets/{budget\_id}/accounts](https://api.ynab.com/v1#/Accounts/createAccount)

Create a new account

GET[/budgets/{budget\_id}/accounts/{account\_id}](https://api.ynab.com/v1#/Accounts/getAccountById)

Single account

### [Categories](https://api.ynab.com/v1#/Categories)

The categories for a budget

GET[/budgets/{budget\_id}/categories](https://api.ynab.com/v1#/Categories/getCategories)

List categories

GET[/budgets/{budget\_id}/categories/{category\_id}](https://api.ynab.com/v1#/Categories/getCategoryById)

Single category

PATCH[/budgets/{budget\_id}/categories/{category\_id}](https://api.ynab.com/v1#/Categories/updateCategory)

Update a category

GET[/budgets/{budget\_id}/months/{month}/categories/{category\_id}](https://api.ynab.com/v1#/Categories/getMonthCategoryById)

Single category for a specific budget month

PATCH[/budgets/{budget\_id}/months/{month}/categories/{category\_id}](https://api.ynab.com/v1#/Categories/updateMonthCategory)

Update a category for a specific month

### [Payees](https://api.ynab.com/v1#/Payees)

The payees for a budget

GET[/budgets/{budget\_id}/payees](https://api.ynab.com/v1#/Payees/getPayees)

List payees

GET[/budgets/{budget\_id}/payees/{payee\_id}](https://api.ynab.com/v1#/Payees/getPayeeById)

Single payee

PATCH[/budgets/{budget\_id}/payees/{payee\_id}](https://api.ynab.com/v1#/Payees/updatePayee)

Update a payee

### [Payee Locations](https://api.ynab.com/v1#/Payee%20Locations)

When you enter a transaction and specify a payee on the YNAB mobile apps, the GPS coordinates for that location are stored, with your permission, so that the next time you are in the same place (like the Grocery store) we can pre-populate nearby payees for you! It’s handy and saves you time. This resource makes these locations available. Locations will not be available for all payees.

GET[/budgets/{budget\_id}/payee\_locations](https://api.ynab.com/v1#/Payee%20Locations/getPayeeLocations)

List payee locations

GET[/budgets/{budget\_id}/payee\_locations/{payee\_location\_id}](https://api.ynab.com/v1#/Payee%20Locations/getPayeeLocationById)

Single payee location

GET[/budgets/{budget\_id}/payees/{payee\_id}/payee\_locations](https://api.ynab.com/v1#/Payee%20Locations/getPayeeLocationsByPayee)

List locations for a payee

### [Months](https://api.ynab.com/v1#/Months)

Each budget contains one or more months, which is where Ready to Assign, Age of Money and category (budgeted / activity / balances) amounts are available.

GET[/budgets/{budget\_id}/months](https://api.ynab.com/v1#/Months/getBudgetMonths)

List budget months

GET[/budgets/{budget\_id}/months/{month}](https://api.ynab.com/v1#/Months/getBudgetMonth)

Single budget month

### [Transactions](https://api.ynab.com/v1#/Transactions)

The transactions for a budget

GET[/budgets/{budget\_id}/transactions](https://api.ynab.com/v1#/Transactions/getTransactions)

List transactions

POST[/budgets/{budget\_id}/transactions](https://api.ynab.com/v1#/Transactions/createTransaction)

Create a single transaction or multiple transactions

PATCH[/budgets/{budget\_id}/transactions](https://api.ynab.com/v1#/Transactions/updateTransactions)

Update multiple transactions

POST[/budgets/{budget\_id}/transactions/import](https://api.ynab.com/v1#/Transactions/importTransactions)

Import transactions

GET[/budgets/{budget\_id}/transactions/{transaction\_id}](https://api.ynab.com/v1#/Transactions/getTransactionById)

Single transaction

PUT[/budgets/{budget\_id}/transactions/{transaction\_id}](https://api.ynab.com/v1#/Transactions/updateTransaction)

Updates an existing transaction

DELETE[/budgets/{budget\_id}/transactions/{transaction\_id}](https://api.ynab.com/v1#/Transactions/deleteTransaction)

Deletes an existing transaction

GET[/budgets/{budget\_id}/accounts/{account\_id}/transactions](https://api.ynab.com/v1#/Transactions/getTransactionsByAccount)

List account transactions

GET[/budgets/{budget\_id}/categories/{category\_id}/transactions](https://api.ynab.com/v1#/Transactions/getTransactionsByCategory)

List category transactions, excluding any pending transactions

GET[/budgets/{budget\_id}/payees/{payee\_id}/transactions](https://api.ynab.com/v1#/Transactions/getTransactionsByPayee)

List payee transactions, excluding any pending transactions

GET[/budgets/{budget\_id}/months/{month}/transactions](https://api.ynab.com/v1#/Transactions/getTransactionsByMonth)

List transactions in month, excluding any pending transactions

### [Scheduled Transactions](https://api.ynab.com/v1#/Scheduled%20Transactions)

The scheduled transactions for a budget

GET[/budgets/{budget\_id}/scheduled\_transactions](https://api.ynab.com/v1#/Scheduled%20Transactions/getScheduledTransactions)

List scheduled transactions

POST[/budgets/{budget\_id}/scheduled\_transactions](https://api.ynab.com/v1#/Scheduled%20Transactions/createScheduledTransaction)

Create a single scheduled transaction

GET[/budgets/{budget\_id}/scheduled\_transactions/{scheduled\_transaction\_id}](https://api.ynab.com/v1#/Scheduled%20Transactions/getScheduledTransactionById)

Single scheduled transaction

#### Schemas

ErrorResponse

ErrorDetail

UserResponse

User

DateFormat

CurrencyFormat

BudgetSummaryResponse

BudgetSummary

BudgetDetailResponse

BudgetDetail

BudgetSettingsResponse

BudgetSettings

AccountsResponse

AccountResponse

Account

PostAccountWrapper

SaveAccount

LoanAccountPeriodicValue

AccountType

CategoriesResponse

CategoryResponse

CategoryGroupWithCategories

CategoryGroup

Category

SaveCategoryResponse

PayeesResponse

PayeeResponse

SavePayeeResponse

Payee

PayeeLocationsResponse

PayeeLocationResponse

PayeeLocation

TransactionsResponse

HybridTransactionsResponse

PutTransactionWrapper

PostTransactionsWrapper

PatchTransactionsWrapper

ExistingTransaction

NewTransaction

SaveTransactionWithIdOrImportId

SaveTransactionWithOptionalFields

SaveSubTransaction

SaveTransactionsResponse

TransactionResponse

TransactionSummary

TransactionDetail

HybridTransaction

PatchPayeeWrapper

SavePayee

PatchCategoryWrapper

SaveCategory

PatchMonthCategoryWrapper

SaveMonthCategory

TransactionsImportResponse

BulkResponse

BulkTransactions

SubTransaction

ScheduledTransactionsResponse

ScheduledTransactionResponse

PostScheduledTransactionWrapper

SaveScheduledTransaction

ScheduledTransactionSummary

ScheduledTransactionDetail

ScheduledSubTransaction

MonthSummariesResponse

MonthDetailResponse

MonthSummary

MonthDetail

TransactionFlagColor

TransactionFlagName

TransactionClearedStatus

ScheduledTransactionFrequency

