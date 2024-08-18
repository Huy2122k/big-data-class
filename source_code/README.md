# Lecture note

## Step by step to run a cluster
+ Chạy master node trên môt máy, ví dụ tại 192.168.0.100 (master-spark)
+ Sửa file docker-compose.yml để định nghĩa SPARK_MASTER=spark://master-spark:7077
+ Chỉnh master-spark:192.168.0.100
+ Build spark_master image: docker-compose build spark_master
+ Run bash: docker exec -it spark_master bash

+ Chỉnh spark interpreter của Zeppelin trong: http://localhost/#/interpreter thành spark://192.168.0.100:7077


+ Cài elasticsearch để lưu trữ dữ liệu: docker-compose up -d --build elasticsearch

+ Cài kafka để trung chuyển dữ liệu từ crawler: docker-compose up -d --build zookeeper kafka


+ test thử kafka:
kafka-topics.sh --list --zookeeper zookeeper:2181

kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list "kafka:9092" --topic "amazon-laptops" --time -1

kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic "amazon-laptops" --from-beginning



++++++ chạy master ++++++

/usr/spark-2.2.0/sbin/start-master.sh

++++++ Chạy worker kết nối vào master ++++++

/usr/spark-2.2.0/sbin/start-slave.sh spark://master:7077

++++++ submit job spark streaming kafka ++++++
// mount code in folder notebook
cd notebook 

spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 consumer.py --master spark://master:7077

++++++ chạy Crawler ++++++

python CrawlData.py --st 1 --end 10