import pandas as pd

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression

def to_spark_df(fin):
    df = pd.read_csv(fin)
    df.fillna("", inplace=True)
    df = hc.createDataFrame(df)
    return (df)

    # Load the train-test sets


train = to_spark_df("../input/train.csv")  #TODO Add the file address here
test = to_spark_df("../input/test.csv")    #TODO Add the file address here

out_cols = [i for i in train.columns if i not in ["id", "comment_text"]]

# Sadly the output is not as  pretty as the pandas.head() function
train.show(5)

# View some toxic comments
train.filter(F.col('toxic') == 1).show(5)


# Basic sentence tokenizer
tokenizer = Tokenizer(inputCol="comment_text", outputCol="words")
wordsData = tokenizer.transform(train)

# Count the words in a document
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures")
tf = hashingTF.transform(wordsData)

tf.select('rawFeatures').take(2)

# Build the idf model and transform the original token frequencies into their tf-idf counterparts
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(tf)
tfidf = idfModel.transform(tf)

tfidf.select("features").first()

REG = 0.1

lr = LogisticRegression(featuresCol="features", labelCol='toxic', regParam=REG)

tfidf.show(5)

lrModel = lr.fit(tfidf.limit(5000))

res_train = lrModel.transform(tfidf)

res_train.select("id", "toxic", "probability", "prediction").show(20)

res_train.show(5)

extract_prob = F.udf(lambda x: float(x[1]), T.FloatType())

(res_train.withColumn("proba", extract_prob("probability"))
 .select("proba", "prediction")
 .show())


test_tokens = tokenizer.transform(test)
test_tf = hashingTF.transform(test_tokens)
test_tfidf = idfModel.transform(test_tf)


test_res = test.select('id')
test_res.head()


test_probs = []
for col in out_cols:
    print(col)
    lr = LogisticRegression(featuresCol="features", labelCol=col, regParam=REG)
    print("...fitting")
    lrModel = lr.fit(tfidf)
    print("...predicting")
    res = lrModel.transform(test_tfidf)
    print("...appending result")
    test_res = test_res.join(res.select('id', 'probability'), on="id")
    print("...extracting probability")
    test_res = test_res.withColumn(col, extract_prob('probability')).drop("probability")
    test_res.show(5)

test_res.show(5)

test_res.coalesce(1).write.csv('./results/spark_lr.csv', mode='overwrite', header=True)
