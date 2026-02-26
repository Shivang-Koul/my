
CREATE EXTERNAL TABLE IF NOT EXISTS applications_logs (
  date_time STRING,
  location STRING,
  bytes INT,
  request_ip STRING,
  method STRING,
  host STRING,
  uri STRING,
  status INT,
  referrer STRING,
  os STRING,
  browser STRING,
  browser_version STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  "input.regex" = "^(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\s+(\\S+)\\s+(\\d+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\d+)\\s+(\\S*)\\s+some-data\\(([^;]+);\\s*([^\\)]+)\\)%20([^\\/]+)\\/(\\S+)$",
  "input.regex.case.insensitive" = "false"
)
STORED AS TEXTFILE
LOCATION 's3://cloudage.llc/data/';

-- Query to analyze OS distribution
INSERT OVERWRITE DIRECTORY 's3://cloudage.llc/output/os_requests/'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
  os,
  COUNT(*) AS count
FROM applications_logs
WHERE date_time BETWEEN '2014-07-05' AND '2025-08-05'
GROUP BY os;