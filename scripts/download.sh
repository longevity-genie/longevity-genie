#!/bin/bash

# Read URLs from file line by line
while IFS= read -r line
do
    # Extract the filename
    filename=$(echo $line | awk -F'/' '{print $NF}' | awk -F'?' '{print $1}')

    # Download file with wget, -nc prevents re-downloading existing files
    wget -nc -O $filename "$line"
done < files.txt
wget -nc -O 20230714_111942_00012_e64uq_fa26c0dd-5c6d-4f66-a159-86f3013e2f9c.gz https://ai2-s2ag.s3.amazonaws.com/staging/2023-07-11/s2orc/20230714_111942_00012_e64uq_fa26c0dd-5c6d-4f66-a159-86f3013e2f9c.gz?AWSAccessKeyId=ASIA5BJLZJPWSL2B76RW&Signature=A5yUpBUeT5X6pVbHNaoI%2BmWliaU%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIGF5eAZmPhEA4ljc%2B7U4PcsX%2BcY7CPwFQRQ6s9quUcobAiEAg5eYYsfn3WMoZq4IIe2HjbAk0WmkEjxP1yzjgtUcPpcq%2FwMIPxAAGgw4OTYxMjkzODc1MDEiDC%2FfGCWFRWWatCTJmSrcAwIv6HKG2EbZrnkkXh%2FSABs1Q0xXLuFOZpZDN3OW4cstw4etgH%2FSZHDG7xo1E%2Fa2v4Kbne1jmFxOVFyzv8%2FXijiRCAHlS6OR%2F%2B3Dnjru9RKwDGU3pKRg9SC7RxU6lsGHHzMlve6mNNMgdmth57BLRAgMqLlf%2B20YXgiL5kRfb6FFHd%2BU2rS2WvTgG2RdJiRohVT9IuEpg4qUZILCADDbKIvUxbq6ECxbpqjvw7oYS6hIgTspYO%2BZtHpxoEuwFF6i29%2BXtH6nPviElxsCJLH0useT1JgOmiSOSrp9IkIyf%2BcZ6NF0s445r0Ob8gRhlq0q7x7Ptt72uTisSaul1emWg8DET76mFrEetRSsZru7KLOV7HK0%2FEySIcVEKb5eHn6RACPTVNZde99LFxWa2O4tRh8iS5YvbmClKSz8uvxLhTGDYs0jLpbkleCdqQjo%2FeT5sfzNg1fehnMmRWMjt1vjaUVTfCAAwRsL6cYzsbi%2Fqvm%2FaU0kTxyRtftZMDc6qHPrrPWkJ%2F3KmwZr%2B8b7PYYjpCiXmlI9RlcSdzpFPN9rmk3W61YAQOsEWuYiQx6uu3FU6Dqo0sGrDfpDVLVe7ZlisC1BP34EEUBK%2FwlMno93zPd7xG%2FWk%2Fr0%2B6D1KgPsMNqMzqUGOqUBLvMec8k43qkYEof9y%2F1b5wiUJbmu5f4%2B3pWwHoA%2FZYt6EhbiqEGWbbJcbqEejBzkd6rgFH8zvQHfEL0qhobD0zmY0YFtb5ctff6msHdYoQLvdfHqp2BKLNPRmPlPeh410NgyxZsZXOyklew4o67JLB9Wq2rz3glGg11sau6SWfA8Fxxuc9vM3TYNE9lAm6%2FDquEJIuA%2FKc37laDAnRHGJ090fRSx&Expires=1690106807