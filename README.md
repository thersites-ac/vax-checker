# Vax-Checker

### What it does
Checks for vaccine appointments for certain pharmacies in PA and notifies you when it finds one.

### How to use
You will need to provision an EC2 instance. Ssh into the instance, then create a file called `.env` and fill it with `export KEY=VALUE` statements to populate the following environment variables:
  * AWS programmatic access credentials
  * AWS region
  * comma-separated list of emails (e.g. `dude@earthlink.net,walter@netscape.com,donny@aol.com`)
  * zip code

Next, run

    sudo su
    yum update
    yum install -y git 
    yum install -y docker
    git clone https://www.github.com/thersites-ac/vax-checker
    cd vax-checker
    ./launch CVS 
    ./launch RiteAid

The script `launch` creates Docker processes to query the pharmacy URLs every 30 seconds. If an appointment becomes available, you get an SNS notification. Deploying new changes consists of running `docker stop <container id>` followed by `./launch <CVS or RiteAid>`.

Appointment check queries happen every 30 seconds. The result of each query is cached, so you don't get a notification every 30 seconds that an appointment slot is open; instead you only get notified the first time it becomes available.
