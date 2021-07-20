# LIBRA on AWS
The experiment to distribute computation requests among EC2 instances and Serverless Function!

To run the experiment, first make sure the configurations are what you want i.e input log file path, ALB url etc.
And then please [setup your AWS credentials with boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#interactive-configuration).
After that run `python3 run_experiment.py`. 

# Files
`run_experiment.py`
```
This is the entry point of this experiment. It establishes services with utility functions and calls manager to generate traffics.
```

Utility Functions(`req_utils.py` `VM_utils.py` and `SimpleLB.py`)
```
Those files contain functions to create EC2 autoscaling group and cloudwatch alarm.
```

`configuration.py`
```
Readers should consider modify the settings of their experiment here.
```

requirements
```
requests
boto3
pytz
```