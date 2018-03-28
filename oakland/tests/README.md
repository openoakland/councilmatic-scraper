Unit Tests for Oakland
======================

How to Run All Tests
--------------------
1. Go to the oakland directory:
```
cd /home/postgres/work/oakland/tests
```
2. Run run_tests.sh:
```
pytest
```

The run_tests.sh script will run all of the pytest files in the /home/postgres/work/oakland/tests directory.

How to Run a Single Test File
-----------------------------
1. Go to the oakland directory:
```
cd /home/postgres/work/oakland/tests
```
2. Run:
```
pytest <<test file>>
```
i.e.
```
pytest test_bills.py
```

How to Run a Single Test
------------------------
1. Go to the oakland directory:
```
cd /home/postgres/work/oakland/tests
```
2. Run:
```
pytest -k <<function name>>
```
i.e.
```
pytest -k "test_does_person_exist"
```
