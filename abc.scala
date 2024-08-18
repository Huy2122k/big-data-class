import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import org.apache.spark.streaming.dstream.DStream
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark._
import org.apache.spark.streaming._
import org.apache.spark.streaming.StreamingContext._ // not necessary since Spark 1.3

object LogAnalyzerStreaming{
    def main(args: Array[String]){
        val WINDOW_LENGTH = Seconds(30)
	val SLIDE_INTERVAL = Seconds(10)

	val sparkConf = new SparkConf().setAppName("Log Analyzer Streaming in Scala")
	val streamingContext = new StreamingContext(sparkConf, SLIDE_INTERVAL)

	val logLinesDStream: DStream[String] = streamingContext.socketTextStream("127.0.0.1", 8888)

	val accessLogsDStream: DStream[ApacheAccessLog] = logLinesDStream.map(ApacheAccessLog.parseLogLine).cache()

	val windowDStream: DStream[ApacheAccessLog] = accessLogsDStream.window(WINDOW_LENGTH, SLIDE_INTERVAL)


	windowDStream.foreachRDD(accessLogs => {
	    if(accessLogs.count() == 0){
		println("No access logs received in this time interval")
	    } else {
		val contentSizes: RDD[Long] = accessLogs.map(_.contentSize).cache()
		println("Content Size Avg: %s, Min: %s, Max: %s".format(contentSizes.reduce(_+_) / contentSizes.count, contentSizes.min, contentSizes.max))

		val responseCodeToCount: Array[(Int, Long)] = accessLogs.map(_.responseCode -> 1L).reduceByKey(_+_).take(100)
		println(s"""Response code counts: ${responseCodeToCount.mkString("[", ",", "]")}""")

		val ipAddresses: Array[String] = accessLogs.map(_.ipAddress -> 1L).reduceByKey(_+_).filter(_._2 > 10).map(_._1).take(100)
		println(s"""IPAddresses > 10 times: ${ipAddresses.mkString("[", ",", "]")}""")

		val topEndpoints: Array[(String, Long)] = accessLogs.map(_.endpoint -> 1L).reduceByKey(_+_).top(10)(Ordering.by[(String, Long), Long](_._2))
		println(s"""Top Endpoints: ${topEndpoints.mkString("[", ",", "]")}""")
	    }
	})

	streamingContext.start()
        streamingContext.awaitTermination()
    }
}