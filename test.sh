#!/bin/bash
source ../../env.sh
/usr/local/hadoop/bin/hdfs dfs -rm -r /toxiccomments/input/
/usr/local/hadoop/bin/hdfs dfs -mkdir -p /toxiccomment/input/
/usr/local/hadoop/bin/hdfs dfs -copyFromLocal ../../test-data/toxiccomment.py /toxiccomment/input/
/usr/local/spark/bin/spark-submit --master=spark://$SPARK_MASTER:7077 ./toxiccomment.py hdfs://$SPARK_MASTER:9000/toxiccomment/input/
