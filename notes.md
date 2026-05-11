## Service
- Multithreaded (I/O bound)
- Fixed worker size, queue for transactions
- Lock to prevent race conditions

## Flask
- Templates for transaction, account details, success/failure screens, form for transaction

## Analysis
- Compare worker counts, plot on matplotlib
- Test over 10, 100, 1000 concurrent transactions


# To Do
1. Get service up and running (barebones)
2. Get Flask routes and templates to display back end
3. Validation
4. Extra features?