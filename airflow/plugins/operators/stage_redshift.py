
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
#from helpers import SqlQueries


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields=("s3_key",)
    sql_copy="""
            COPY {}
            FROM '{}'
            ACCESS_KEY_ID '{}'
            SECRET_ACCESS_KEY '{}'
            FORMAT AS JSON {}
            """
    
    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials="",
                 table="",
                 s3_bucket="",
                 s3_key="",
                 file_format="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials=aws_credentials
        self.table=table
        self.s3_bucket=s3_bucket
        self.s3_key=s3_key
        self.file_format=file_format
        
    def execute(self, context):
        self.log.info('StageToRedshiftOperator not implemented yet')
        
        aws_hook=AwsHook(self.aws_credentials)
        aws_credentials=aws_hook.get_credentials()
        redshift=PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info("Clearing data from table")
        redshift.run("DELETE FROM {}".format(self.table))
        
        self.log.info("Data copy from S3 to Redshift")
        rendered_key=self.s3_key.format(**context)
        s3_path="s3://{}/{}".format(self.s3_bucket, rendered_key)
        ##self.s3_prefix)
        sql_stmt=StageToRedshiftOperator.sql_copy.format (self.table,
                                                       s3_path, 
                                                       aws_credentials.access_key, 
                                                       aws_credentials.secret_key,
                                                       self.file_format)

        redshift.run(sql_stmt)




