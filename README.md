# Vax-Checker

### What it does
Checks for vaccine appointments for certain pharmacies in PA and notifies you when it finds one.

### How to use
You will need to provision an EC2 instance. Then, see the `bootstrap.sh` script. This is more descriptive than useful, because the run scripts require the following (missing) environment variables:
  * AWS programmatic access credentials
  * AWS region
  * comma-separated list of emails
  * comma-separated list of phone numbers--this currently does nothing, because the SMS notifications aren't going tnrough.
  * zip code

The bootstrap script installs dependencies on your EC2 instance, then starts up Docker processes to query the pharmacy URLs every 30 seconds. If an appointment is available, it notifies you with SNS notifications.
