# Mini Pupper Regression Tests

This directory contains toools and test scripts to test the Stanford controller for mini pupper

## Testing Strategy

The hardware is abstracted by Python APIs that are installed with the repo min_pupper_bsp. Each of the APIs has a mock version that dumps information to a
log file. The user input is provided with a joystick. We use a joystick simulator to simulate user action.

The Stanford controller is started as a thread, we then send a sequence of joystick commands and compare the resulting calls to the hardware with expected output.

When developing test cases we will run each test case on a physical mini pupper and observe the behavior. If we determine that is is correct behavor we run
the test case in a virtual environment with the mock API and record the calls to the API which will be used as expected results for future test runs.

## Test Environment

These tests need to be run in a virtual Ubuntu 22.04 machine that can be recreated any time. During development we will separate the installation of the environment from running the tests but in the final setup we will have a test runner that spans a virtual machine, configure the test environment, runs the test and records the test results before deleting the virtual machine. This automated test will be triggered by git.

To install the test environment run on your plain vanilla Ubuntu 22.04 machine the command

```
$ ./install_test_environment.sh
```

## Running the Tests

To run the test run the command

```
$ ./run_all_tests.sh
```
