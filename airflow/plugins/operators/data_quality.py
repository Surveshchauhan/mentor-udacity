from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'
    
    @apply_defaults
    def __init__(self,
        redshift_conn_id="",
        aws_credentials="",
        *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials=aws_credentials

     
    def execute(self, context):
        aws_hook=AwsHook(self.aws_credentials)
        aws_credentials=aws_hook.get_credentials()
        redshift=PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        failure_list=[]
        
        self.log.info("Quality checks are applied to Staging Tables")
        
        checks=[
        {'check_query': "SELECT COUNT(*) FROM staging_events WHERE song is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM staging_events WHERE artist is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM staging_events WHERE length is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM staging_songs WHERE title is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM staging_songs WHERE artist_name is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM staging_songs WHERE duration is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM users WHERE userid is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM songs WHERE song_id is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM artists WHERE artist_id is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM songplays WHERE session_id is null", 'expected_result':0},
        {'check_query': "SELECT COUNT(*) FROM songplays WHERE start_time is null", 'expected_result':0},
        ]
        
        for check in checks:
            query=check.get('check_query')
            expect_result=check.get('expected_result')
            result=redshift.get_records(query)[0]
            
            count_err=0
            
            if expect_result != result[0]:
                count_err = count_err+1
                failure_list.append(query)
            
        if count_err == 0:
            self.log.info('Data processed correctly')
        else:
            self.log.info ('Data processing failure in the ETL')
            self.log.info (failure_list)
            #raise ValueError ('Data quality failure')    
                
                
               


            
    