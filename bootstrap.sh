# almost the entire bootstrap sequence -- does not set environment variables
sudo su
yum update
yum install -y git
yum install -y docker
git clone https://www.github.com/thersites-ac/vax-checker
cd vax-checker
./launch CVS
./launch RiteAid
