Unit Tests for Oakland
======================

How to Run All Tests
--------------------
1. Go to the oakland directory:
```
cd /home/postgres/work/oakland
```
2. Run run_tests.sh:
```
./run_tests.sh
```

The run_tests.sh script will run all of the pytest files in the /home/postgres/work/oakland/tests directory.

How to Run a Single Test File
-----------------------------
1. Go to the oakland directory:
```
cd /home/postgres/work/oakland
```
2. Set Python path:
```
export PYTHONPATH=.
```
3. Run:
```
py.test tests/<<test file>>
```
i.e.
```
py.test tests/test_bills.py
```
