import os
import io
import sys
import json
import random
import base64
import requests
from PIL import Image
from all_models import *
from loguru import logger
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from generate_image import GenerateImage
from pebble import ProcessPool
from multiprocessing import Process, Manager, Value
from functools import partial

load_dotenv()

app = Flask(__name__)
CORS(app)

class HasuraInline:
    @staticmethod
    def execute_query(graphql_query, query_variables=None):
        try:
            # Log the execution of the query
            logger.debug("execute_query")
            # Prepare the headers for the request
            headers = {"x-hasura-admin-secret": HasuraInline.HASURA_ADMIN_SECRET}
            
            # Prepare the payload for the request
            payload = {
                'query': graphql_query,
                'variables': query_variables
            }

            # Log the payload
            # logger.debug(payload)

            # Send the POST request to the Hasura URL
            response = requests.post(HasuraInline.HASURA_URL, json=payload, headers=headers)

            # Check if the request was successful
            if response.status_code != 200:
                # Raise an exception if the request was not successful
                raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.json()}")

            if "errors" in response.json():
                return {"success": False, "message": response.json()}

            # Return the JSON response
            return {"success": True, "message": response.json()}
        except Exception as error:
            # Log the error and return None
            logger.error(f"An error occurred while executing the query: {str(error)}")
            return {"success": False, "message": str(error)}

    # Define a method to insert data into a table
    @staticmethod
    def insert(table_info, data=None):
        try:
            # Check if data is not None
            if data is None:
                # Raise a ValueError if data is None
                raise ValueError("Data for insertion cannot be None.")

            update_columns = ','.join([
                column['name'] 
                for column in table_info['columns'] 
                if not "update" in column or column['update'] != False
            ])
            # Construct the mutation query string
            mutation_query = f"""
                mutation insert_{table_info['table']}($objects: [{table_info['table']}_insert_input!]!) {{
                    insert_{table_info['table']}(objects: $objects, 
                    on_conflict: {{
                        constraint: {table_info['constraint']}, 
                        update_columns: [
                            {update_columns}
                        ]}}) {{
                    returning {{
                        {','.join([column['name'] for column in table_info['columns']])}
                    }}
                }}
            }}
            """

            # Remove \n from query
            mutation_query = mutation_query.replace("\n", "")

            # Prepare the variables for the query
            mutation_variables = {"objects": data}

            # Execute the query and get the response
            response = HasuraInline.execute_query(mutation_query, mutation_variables)
            
            # Check if there are any errors in the response
            if not response["success"]:
                # Log the error message
                logger.error(response['message'])
                return {"success": False, "message": response['message']}
            
            # Return the response
            return {"success": True, "message": response['message']}
        except Exception as error:
            # Log the error and return None
            logger.error(f"An error occurred: {str(error)}")
            return {"success": False, "message": str(error)}

    # Define a method to list data from a table
    @staticmethod
    def list(table_info, data=None):
        try:
            # Initialize an empty string for order_by
            order_by = ""
            # Check if "order_by" is in table_info
            if "order_by" in table_info:
                # Set order_by to the order_by in table_info
                order_by = table_info['order_by']
                # Format order_by
                order_by = f", order_by: {{ {order_by['column']}: {order_by['order']} }}"

            # Construct the query string
            list_query = f"""
                        query get_{table_info['table']}($limit: Int!, $offset: Int!) {{
                          {table_info['table']}(limit: $limit, offset: $offset {order_by}) {{
                            {','.join([column['name'] for column in table_info['columns']])}
                          }}
                        }}
                    """
            # Check if data is None
            if data is None:
                # Set default values for limit and offset
                data = {"limit": 100, "offset": 0}
            # Prepare the variables for the query
            query_variables = data
            # Execute the query and get the response
            response = HasuraInline.execute_query(list_query, query_variables)

            # Check if there are any errors in the response
            if not response["success"]:
                # Log the error message
                logger.error(response['message'])
                return {"success": False, "message": response['message']}
            
            # Chcek if errors in the response
            if "errors" in response["message"]:
                logger.error(response['message'])
                return {"success": False, "message": response['message']}
            
            # Return the response
            return {"success": True, "message": response['message']}
        except Exception as error:
            # Log the error and return None
            logger.error(f"An error occurred: {str(error)}")
            return {"success": False, "message": str(error)}

    # Define a method to get data from a table by id
    @staticmethod
    def get(table_info, id):
        try:
            # Initialize an empty string for the primary column
            primary_column = ""
            # Iterate over the columns in the table information
            for column in table_info['columns']:
                # Check if the current column is the primary key
                if "primary_key" in column and column['primary_key']:
                    # If it is, set the primary column to the name of the current column
                    primary_column = column['name']
                    # Break the loop as we've found the primary key
                    break
            # If no primary key was found in the columns, raise a ValueError
            if primary_column == "":
                raise ValueError("Primary key not found.")

            # Construct the query string
            get_query = f"""
                        query get_{table_info['table']}($id: Int!) {{
                        {table_info['table']}_by_pk({primary_column}: $id ) {{
                            {','.join([column['name'] for column in table_info['columns']])}
                        }}
                        }}
                    """
            # Prepare the variables for the query
            query_variables = {"id": id}
            # Execute the query and get the response
            response = HasuraInline.execute_query(get_query, query_variables)

            # Check if there are any errors in the response
            if not response["success"]:
                # Log the error message
                logger.error(response['message'])
                return {"success": False, "message": response['message']}

            # Return the response
            return {"success": True, "message": response['message']}
        except Exception as error:
            # Log the error and return None
            logger.error(f"An error occurred: {str(error)}")
            return {"success": False, "message": str(error)}

    # Define a method to get data from a table by column value pair
    @staticmethod
    def get_by_columns_value_pair(table_info, columns_value_pair):
        try:
            # Initialize an empty string for columns_value_data
            columns_value_data = ""
            # Iterate over the columns_value_pair
            for column_data in columns_value_pair:
                # Format columns_value_data
                if type(column_data['value']) == str:
                    columns_value_data += f"{column_data['column_name']}: {{{column_data['operator']}: \"{column_data['value']}\"}}, "
                if type(column_data['value']) == list:
                    columns_value_data += f"{column_data['column_name']}: {{{column_data['operator']}: {json.dumps(column_data['value'])}}}, "

            # Remove trailing comma and space from columns_value_data
            columns_value_data = columns_value_data.strip().strip(",")

            # Construct the query string
            get_by_column_query = f"""
                query get_{table_info['table']}{{
                  {table_info['table']}(where: {{ {columns_value_data} }}) {{
                    {','.join([column['name'] for column in table_info['columns']])}
                  }}
                }}
            """
            # Execute the query and get the response
            response = HasuraInline.execute_query(get_by_column_query)
            
            # Check if there are any errors in the response
            if not response["success"]:
                # Log the error message
                logger.error(response['message'])
                # If the response is not successful, log the error message and return a failure response
                return {"success": False, "message": response['message']}

            # If the response is successful, return a success response
            return {"success": True, "message": response['message']}
        except Exception as error:
            # If an exception occurs, log the error and return a failure response
            logger.error(f"An error occurred: {str(error)}")
            return {"success": False, "message": str(error)}

    @staticmethod
    def delete(table_info, ids):
        try:
            # Initialize an empty string for the primary column
            primary_column = ""
            # Iterate over the columns in the table information
            for column in table_info['columns']:
                # Check if the current column is the primary key
                if "primary_key" in column and column['primary_key']:
                    # If it is, set the primary column to the name of the current column
                    primary_column = column['name']
                    # Break the loop as we've found the primary key
                    break
            # If no primary key was found in the columns, raise a ValueError
            if primary_column == "":
                raise ValueError("Primary key not found.")

            # Construct the query string
            delete_query = f"""
                        mutation delete_{table_info['table']}($ids: [Int!]!) {{
                            delete_{table_info['table']}(where: {{{primary_column}: {{_in: $ids }} }} ) {{
                                affected_rows
                            }}
                        }}
                    """
            # Prepare the variables for the query
            query_variables = {"ids": ids}
            # Execute the query and get the response
            response = HasuraInline.execute_query(delete_query, query_variables)

            # Check if there are any errors in the response
            if not response["success"]:
                # Log the error message
                logger.error(response['message'])
                return {"success": False, "message": response['message']}

            # Return the response
            return {"success": True, "message": response['message']}
        except Exception as error:
            # Log the error and return None
            logger.error(f"An error occurred: {str(error)}")
            return {"success": False, "message": str(error)}


# Env variable 
HasuraInline.HASURA_URL = os.getenv('HASURA_URL', "")
HasuraInline.HASURA_ADMIN_SECRET = os.getenv('HASURA_ADMIN_SECRET', "")

def load_templates():
    try:
        templates = HasuraInline.list(TEMPLATES_TABLE_INFO)
        if templates['success']:
            return templates['message']['data']['templates']
    except Exception as ex:
        return {"success": False, "message": str(ex)}
    return {"success": False, "message": "Error load tempaltes."}

def load_tags():
    try:
        tags = HasuraInline.list(TAGS_TABLE_INFO)
        if tags['success']:
            return tags['message']['data']['tags']
    except Exception as ex:
        return {"success": False, "message": str(ex)}
    return {"success": False, "message": "Error load tempaltes."}

def load_tags_templates_mapping():
    try:
        tags_templates_mapping = HasuraInline.list(TAGS_TEMPLATES_MAPPING_TABLE_INFO)
        if tags_templates_mapping['success']:
            return tags_templates_mapping['message']['data']['tags_templates_mapping']
    except Exception as ex:
        return {"success": False, "message": str(ex)}
    return {"success": False, "message": "Error load tempaltes."}

@app.route('/')
def home():
    tags_templates_mapping = load_tags_templates_mapping()
    tags = load_tags()
    templates = load_templates()
    templates_data = []
    for template in templates:
        template_id = template['template_id']

        tags_data = []
        tag_names = ""
        for ttm in tags_templates_mapping:
            if ttm['template_id'] == template_id:
                tag = next((tag for tag in tags if tag['tag_id'] == ttm['tag_id']), None)
                tag_names += tag['tag_name'] + " "
                tags_data.append(tag)

        template_json = json.loads(template['template_json'])
        template_name = template['template_name'].rsplit(" - ", 1)[0]
        updated_template = {
            **template, 
            'template_name': template_name,
            'template_json': template_json, 
            'tags': tags_data,
            'tag_names': tag_names
        }
        templates_data.append(updated_template)

    data = {}
    data['templates'] = templates_data
    data['tags'] = tags

    return render_template('layout.html', data=data)

@app.route('/save', methods=['POST'])
def save():
    try:
        logger.debug("save")
        json_data = request.get_json()
        # logger.debug(json_data)
        if "template_name" not in json_data:
            return "Template Name Missing", 406
        if "image_tags" not in json_data or not json_data['image_tags']:
            return "Image Tags are required", 409

        # Get column names in an array list
        templates_column_names = [column['name'] for column in TEMPLATES_TABLE_INFO['columns']]
        
        templates_table_data = {}
        for column in json_data:
            if column in templates_column_names:
                templates_table_data.update({column: json_data[column]}) 

        templates_table_data.update({"status": "ACTIVE"})
        # Add width x height to template_name 
        templates_table_data['template_name'] = f"{json_data['template_name']} - {json_data['template_width']}x{json_data['template_height']}"
        saved_templates_data = HasuraInline.insert(TEMPLATES_TABLE_INFO, templates_table_data)
        if not saved_templates_data['success']:
            return 'Error : ' + str(saved_templates_data['message']), 409

        tags_table_data = []
        for image_tag in json_data['image_tags']:
            image_tag_dict = {
                "tag_name": image_tag,
                "status": "ACTIVE"
            }
            tags_table_data.append(image_tag_dict)
        saved_tags_data = HasuraInline.insert(TAGS_TABLE_INFO, tags_table_data)
        if not saved_tags_data['success']:
            return 'Error : ' + str(saved_tags_data['message']), 409
        
        tags_templates_mapping_table_data = []
        template_id = None
        for saved_templates in saved_templates_data['message']['data']['insert_templates']['returning']:
            template_id = saved_templates['template_id']
            
            for saved_tags in saved_tags_data['message']['data']['insert_tags']['returning']:
                tag_id = saved_tags['tag_id']
                tags_templates_mapping_dict = {
                    "tag_id": tag_id,
                    "template_id": template_id
                }
                tags_templates_mapping_table_data.append(tags_templates_mapping_dict)
        
        # Get tags_templates_mapping data for delete
        previousMapping = HasuraInline.get_by_columns_value_pair(
            TAGS_TEMPLATES_MAPPING_TABLE_INFO, [
                {
                    "column_name": "template_id",
                    "value": template_id,
                    "operator": "_eq"
                }
            ]
        )
        if not previousMapping['success']:
            return 'Error : ' + str(previousMapping['message']), 409
        previousMapping = previousMapping['message']['data']['tags_templates_mapping']
        differenceMappingId = []
        mappingIds = [str(mapping['template_id']) + "-" + str(mapping['tag_id']) for mapping in tags_templates_mapping_table_data]
        for previous in previousMapping:
            logger.debug(previous)
            if previous['template_id'] == template_id:
                if str(previous['template_id']) + "-" + str(previous['tag_id']) not in mappingIds:
                    differenceMappingId.append(previous['tags_templates_mapping_id'])
        logger.info(differenceMappingId)
        HasuraInline.delete(TAGS_TEMPLATES_MAPPING_TABLE_INFO, differenceMappingId)

        # Save new mapping id
        saved_tags_templates_mapping_data = HasuraInline.insert(TAGS_TEMPLATES_MAPPING_TABLE_INFO, tags_templates_mapping_table_data)
        if not saved_tags_templates_mapping_data['success']:
            return 'Error : ' + str(saved_tags_templates_mapping_data['message']), 409
        
        return "Success", 200
    except Exception as ex:
        logger.error(ex)
        return ex, 409
    return "Error", 409

@app.route('/upload-image', methods=['POST', 'OPTIONS', 'GET'])
def upload_image():
    receive_data = request.get_json()
    data_url = receive_data['imgData']
    template_name = receive_data['template_name']
    header, encoded = data_url.split(",", 1)
    data = base64.b64decode(encoded)

    image = Image.open(io.BytesIO(data))
    image_path = f"static/files/{template_name}.png"
    image.save(image_path)

    return image_path

@app.route('/template/<template_id>')
def template(template_id):
    template = HasuraInline.get(TEMPLATES_TABLE_INFO, template_id)
    if template['success']:
        template = template['message']['data']['templates_by_pk']['template_json']
        template = json.loads(template)
        return template
    return ""

# Generate images data
@app.route('/generate-google-image', methods=['POST'])
def generate_google_image():
    try:
        json_data = request.get_json()
        no_of_images = json_data['no_of_images']

        # Get ALl Templates        
        templates_info = GenerateImage.get_all_templates_by_tags(json_data, HasuraInline)
        if not templates_info['success']:
            return {"success": False, "message": templates_info['message']}
        templates_info = templates_info['message']

        # Create Circular Templates and Keywords
        circular_templates_info = GenerateImage.create_circular_templates_info(templates_info, no_of_images)

        # Google SERP Data
        google_search_keywords = json_data['google_search_keywords']
        valueserp_api_key = json_data['valueserp']['api_key']

        with Manager() as manager:
            keyword_with_original_image_url = manager.list()
            # Based on all keywords search in google and get all the images with dict format.
            with ProcessPool(max_workers=5, max_tasks=10) as pool:
                for keyword in google_search_keywords:
                    TIMEOUT_SECONDS = 100
                    future = pool.schedule(GenerateImage.get_serp_images_valueserp, 
                                            args=(keyword, valueserp_api_key),
                                            timeout=TIMEOUT_SECONDS)
                    callback = GenerateImage.get_serp_images_valueserp_done(keyword_with_original_image_url)
                    future.add_done_callback(callback)

                used_orignal_image_url = manager.list()

            generated_images = manager.list()
            with ProcessPool(max_workers=5, max_tasks=10) as pool:
                for template in circular_templates_info:
                    try:
                        TIMEOUT_SECONDS = 100
                        future = pool.schedule(GenerateImage.process_template, 
                                            args=(template, keyword_with_original_image_url, used_orignal_image_url),
                                            timeout=TIMEOUT_SECONDS)
                        callback = GenerateImage.process_template_done(generated_images)
                        future.add_done_callback(callback)
                    except Exception as ex:
                        logger.error(ex)

            return {"success": True, "message": list(generated_images)}
    except Exception as error:
        logger.error(f"An error occurred: {str(error)}")
        return {"success": False, "message": str(error)}
    return {"success": False, "message": "Unexpected Errors."}

@app.route('/generate-single-image', methods=['POST'])
def generate_single_image():
    try:
        json_data = request.get_json()
        no_of_images = json_data['no_of_images']

        # Get ALl Templates        
        templates_info = GenerateImage.get_all_templates_by_tags(json_data, HasuraInline)
        if not templates_info['success']:
            return {"success": False, "message": templates_info['message']}
        templates_info = templates_info['message']
        # Create Circular Templates and Keywords
        circular_templates_info = GenerateImage.create_circular_templates_info(templates_info, no_of_images)

        with Manager() as manager:
            used_orignal_image_url = manager.list()

            keyword_with_original_image_url = [
                {
                    "original_image_urls": json_data['image_url'], 
                    "keyword": json_data['keyword'] if 'keyword' in json_data else "image"
                }
            ]

            generated_images = manager.list()
            with ProcessPool(max_workers=5, max_tasks=10) as pool:
                for template in circular_templates_info:
                    try:
                        TIMEOUT_SECONDS = 100
                        future = pool.schedule(GenerateImage.process_template, 
                                            args=(template, keyword_with_original_image_url, used_orignal_image_url),
                                            timeout=TIMEOUT_SECONDS)
                        callback = GenerateImage.process_template_done(generated_images)
                        future.add_done_callback(callback)
                    except Exception as ex:
                        logger.error(ex)
            return {"success": True, "message": list(generated_images)}
    except Exception as error:
        logger.error(f"An error occurred: {str(error)}")
        return {"success": False, "message": str(error)}
    return {"success": False, "message": "Unexpected Errors."}

if __name__ == '__main__':
    app.run(debug=True, port=5000)

