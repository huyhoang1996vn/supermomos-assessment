# database/dynamodb.py
from boto3.dynamodb.conditions import Key
from fastapi import HTTPException
from boto3.dynamodb.conditions import Key, Attr
from functools import reduce
import operator

class DynamoDB:
    def __init__(self, table):
        self.table = table
        
    def create_object(self, object_data: dict):
        try:
            response = self.table.put_item(
                Item=object_data,
                ConditionExpression='attribute_not_exists(id)'
            )
            return object_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_object(self, object_id: str, key_name: str = 'id'):
        response = self.table.get_item(Key={key_name: object_id})
        return response.get('Item')

    def update_object(self, object_id: str, update_data: dict):
        try:
            # Handle reserved keywords by using ExpressionAttributeNames
            expression_names = {}
            expression_values = {}
            update_parts = []
            
            for key, value in update_data.items():
                # Create a placeholder name for the attribute
                placeholder = f"#{key}"
                value_placeholder = f":{key}"
                
                expression_names[placeholder] = key
                expression_values[value_placeholder] = value
                update_parts.append(f"{placeholder}={value_placeholder}")
            
            update_expression = "SET " + ", ".join(update_parts)
            
            print(f"============{update_expression}============")
            print(f"============{expression_values}============")
            print(f"============{expression_names}============")
            
            response = self.table.update_item(
                Key={'id': object_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete_object(self, object_id: str):
        self.table.delete_item(Key={'id': object_id})
        return {"message": "User deleted successfully"}
    
    def get_all_objects(self):
        response = self.table.scan()
        return response.get('Items', [])
    
    def get_object_by_slug(self, slug: str):
        response = self.table.query(
            IndexName='SlugIndex',
            KeyConditionExpression=Key('slug').eq(slug)
        )
        return response.get('Items', [])
    
    def scan_objects(self, filter_expression=None, expression_values=None, expression_names=None, limit=None, last_evaluated_key=None):
        response = self.table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            Limit=limit,
            # ExclusiveStartKey=last_evaluated_key
        )
        return response.get('Items', [])
    
    def query_employees_by_index(
        self,
        company=None,
        job_title=None,
        city=None,
        state=None,
        min_hosted=None,
        max_hosted=None,
        min_attended=None,
        max_attended=None,
        last_evaluated_key=None
    ):

        key_map = {
            'company': {'index': 'CompanyIndex', 'key': 'company', 'value': company, 'operator': 'eq'},
            'jobTitle': {'index': 'JobTitleIndex', 'key': 'jobTitle', 'value': job_title, 'operator': 'eq'},
            'city': {'index': 'CityIndex', 'key': 'city', 'value': city, 'operator': 'eq'},
            'state': {'index': 'StateIndex', 'key': 'state', 'value': state, 'operator': 'eq'},
            'min_hosted': {'index': 'NumberOfEventsHostedIndex', 'key': 'number_of_events_hosted', 'value': min_hosted, 'operator': 'gte'},
            'max_hosted': {'index': 'NumberOfEventsHostedIndex', 'key': 'number_of_events_hosted', 'value': max_hosted, 'operator': 'lte'},
            'min_attended': {'index': 'NumberOfEventsAttendedIndex', 'key': 'number_of_events_attended', 'value': min_attended, 'operator': 'gte'},
            'max_attended': {'index': 'NumberOfEventsAttendedIndex', 'key': 'number_of_events_attended', 'value': max_attended, 'operator': 'lte'}
        }

        index_object = {}
        if company:
            index_object = key_map.get('company')
        elif job_title:
            index_object = key_map.get('jobTitle')
        elif city:
            index_object = key_map.get('city')
        elif state:
            index_object = key_map.get('state')
        
        query_params = {}
        if index_object:
            query_params = {
                'IndexName': index_object.get('index'),
            }
            query_params['KeyConditionExpression'] = Key(index_object.get('key')).eq(index_object.get('value'))
        
        
        # Dynamically build filter expression
        filters = []
        if job_title and index_object.get('key') != 'jobTitle':
            filters.append(Attr('jobTitle').eq(job_title))
        if city and index_object.get('key') != 'city':
            filters.append(Attr('city').eq(city))
        if state and index_object.get('key') != 'state':
            filters.append(Attr('state').eq(state))
        if company and index_object.get('key') != 'company':
            filters.append(Attr('company').eq(company))
        if min_hosted and index_object.get('key') != 'number_of_events_hosted':
            filters.append(Attr('number_of_events_hosted').gte(min_hosted))
        if max_hosted and index_object.get('key') != 'number_of_events_hosted':
            filters.append(Attr('number_of_events_hosted').lte(max_hosted))
        if min_attended and index_object.get('key') != 'number_of_events_attended':
            filters.append(Attr('number_of_events_attended').gte(min_attended))
        if max_attended and index_object.get('key') != 'number_of_events_attended':
            filters.append(Attr('number_of_events_attended').lte(max_attended))
        
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key
        
        if filters:
            query_params['FilterExpression'] = reduce(operator.and_, filters)
        print(f"============{query_params}============")
        # Execute query
        if index_object:
            response = self.table.query(**query_params)
        else:
            response = self.table.scan(**query_params)
        
        return response.get('Items', [])
        
    def get_object_by_index(self, index_name: str, key_name: str, value: str):
        response = self.table.query(
            IndexName=index_name,
            KeyConditionExpression=Key(key_name).eq(value)
        )
        return response.get('Items', [])

