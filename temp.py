import boto3
from boto3.dynamodb.conditions import Key, Attr
from settings import get_dynamodb_resource, ENVIRONMENT 
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(f'Users-{ENVIRONMENT}')

def query_users(filters: dict):
    """
    Enhanced multi-index query function that intelligently selects the best index
    and handles multiple filter combinations efficiently
    """
    # Mapping fields to their index names with priority
    index_map = {
        'email': 'EmailIndex',  # Highest priority - unique
        'company': 'CompanyIndex',
        'jobTitle': 'JobTitleIndex',
        'city': 'CityStateIndex',  # Composite index
        'state': 'CityStateIndex'  # Composite index
    }

    # Define composite indexes and their key structure
    composite_indexes = {
        'CityStateIndex': {
            'hash_key': 'city',
            'range_key': 'state',
            'fields': ['city', 'state']
        }
    }

    # Find the best index to use based on available filters
    best_index = None
    best_key_conditions = {}
    remaining_filters = {}

    # Priority-based index selection
    if 'email' in filters:
        best_index = 'EmailIndex'
        best_key_conditions = {'email': filters['email']}
        remaining_filters = {k: v for k, v in filters.items() if k != 'email'}
        
    elif 'company' in filters:
        best_index = 'CompanyIndex'
        best_key_conditions = {'company': filters['company']}
        remaining_filters = {k: v for k, v in filters.items() if k != 'company'}
        
    elif 'jobTitle' in filters:
        best_index = 'JobTitleIndex'
        best_key_conditions = {'jobTitle': filters['jobTitle']}
        remaining_filters = {k: v for k, v in filters.items() if k != 'jobTitle'}
        
    elif 'city' in filters and 'state' in filters:
        best_index = 'CityStateIndex'
        best_key_conditions = {'city': filters['city'], 'state': filters['state']}
        remaining_filters = {k: v for k, v in filters.items() if k not in ['city', 'state']}
        
    elif 'city' in filters:
        best_index = 'CityStateIndex'
        best_key_conditions = {'city': filters['city']}
        remaining_filters = {k: v for k, v in filters.items() if k != 'city'}
        
    elif 'state' in filters:
        best_index = 'CityStateIndex'
        best_key_conditions = {'state': filters['state']}
        remaining_filters = {k: v for k, v in filters.items() if k != 'state'}

    if not best_index:
        raise ValueError("No suitable index found for the provided filters")

    # Build KeyConditionExpression
    key_condition_parts = []
    for key, value in best_key_conditions.items():
        key_condition_parts.append(Key(key).eq(value))
    
    key_condition_expression = key_condition_parts[0]
    for condition in key_condition_parts[1:]:
        key_condition_expression = key_condition_expression & condition

    # Build FilterExpression for remaining fields
    filter_expression = None
    if remaining_filters:
        filter_parts = []
        for field, value in remaining_filters.items():
            filter_parts.append(Attr(field).eq(value))
        
        filter_expression = filter_parts[0]
        for condition in filter_parts[1:]:
            filter_expression = filter_expression & condition

    # Build query parameters
    query_args = {
        'IndexName': best_index,
        'KeyConditionExpression': key_condition_expression
    }
    
    if filter_expression:
        query_args['FilterExpression'] = filter_expression

    print(f"============Query Args: {query_args}============")
    print(f"============Best Index: {best_index}============")
    print(f"============Key Conditions: {best_key_conditions}============")
    print(f"============Remaining Filters: {remaining_filters}============")
    
    try:
        response = table.query(**query_args)
        return response['Items']
    except Exception as e:
        print(f"============Query Error: {str(e)}============")
        raise

def query_users_advanced(filters: dict, limit: int = 50):
    """
    Advanced version with pagination and better error handling
    """
    try:
        results = query_users(filters)
        return results[:limit]
    except Exception as e:
        print(f"Advanced query failed: {str(e)}")
        # Fallback to scan with filters
        return fallback_scan(filters, limit)

def fallback_scan(filters: dict, limit: int = 50):
    """
    Fallback method using scan when no suitable index is available
    """
    filter_expressions = []
    for field, value in filters.items():
        filter_expressions.append(Attr(field).eq(value))
    
    filter_expression = filter_expressions[0]
    for condition in filter_expressions[1:]:
        filter_expression = filter_expression & condition
    
    response = table.scan(
        FilterExpression=filter_expression,
        Limit=limit
    )
    return response['Items']

# Test cases
if __name__ == "__main__":
    # Test case 1: Company filter
    print("=== Test 1: Company filter ===")
    filters1 = {'company': 'OpenAI'}
    results1 = query_users(filters1)
    print(f"Results: {len(results1)} users found")

    # Test case 2: Company + Job Title
    print("\n=== Test 2: Company + Job Title ===")
    filters2 = {'company': 'OpenAI', 'jobTitle': 'Engineer'}
    results2 = query_users(filters2)
    print(f"Results: {len(results2)} users found")

    # Test case 3: City + State
    print("\n=== Test 3: City + State ===")
    filters3 = {'city': 'San Francisco', 'state': 'CA'}
    results3 = query_users(filters3)
    print(f"Results: {len(results3)} users found")

    # Test case 4: Complex filter
    print("\n=== Test 4: Complex filter ===")
    filters4 = {'company': 'OpenAI', 'jobTitle': 'Engineer', 'city': 'San Francisco'}
    results4 = query_users(filters4)
    print(f"Results: {len(results4)} users found")