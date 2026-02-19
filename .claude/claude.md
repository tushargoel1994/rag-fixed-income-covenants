# Claude Development Guidelines


## AWS
- Boto3 for aws services
- 

## Lambda
- Create all lambda in src/lambda_functions
- create separate folder for each lambda function with handler.py as main file
- Create lambda-specific test in each folder
- Lambda Timeout: 60s
- Memory: 256MB default
- Runtime: Python 3.11
- Create a readme.md file for each lambda with basic lambda functionality (maximum 50 lines)


## Code writing rules
- use Pep8 python code styleguide
- Minimal, Production Ready code
- never hardcode values, use constants instead
- Max funtion length : 30 lines
- Type hints on all functions
- No unnecessary docs or comments
- use f-string for formatting
- Follow AWS Best Practices (boto3, proper error handling)


## Remember
- **Clarity over cleverness** - Code should be obvious to read
- **Document thoroughly** - Future readers (including you) will thank you
- **Reproducibility matters** - Others should be able to replicate your work