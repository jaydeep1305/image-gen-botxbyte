from math import log
import os
import sys
import json
import random
import datetime
import requests
import openai
from all_models import *
from loguru import logger
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import subprocess
from PIL import Image

class PromptServiceInline:
    @staticmethod
    def generate_openai_message(messages, status_object=None):
        try:
            logger.debug("generate_openai_message")
            # Set Azure Configuration
            openai.api_type = os.getenv('AZURE_API_TYPE', "")
            openai.api_version = os.getenv('AZURE_API_VERSION', "")
            openai.api_base = os.getenv('AZURE_API_BASE', "")
            openai.api_key = os.getenv('AZURE_API_KEY', "")

            # Create a chat completion with OpenAI
            completion = openai.ChatCompletion.create(
                engine="gpt35",
                temperature=0.7,
                messages=messages,
                request_timeout=60,
                max_tokens=3000
            )

            # Check if 'choices' is in the completion
            if "choices" in completion:
                if "message" in completion['choices'][0]:
                    if "content" in completion['choices'][0]['message']:
                        generated_message = completion['choices'][0]['message']['content']

                        # Update status if status_object is not None
                        if status_object is not None:
                            status_object['Class'].change_status("SUCCESS_GENERATE_OPENAI_MESSAGE", status_object['try_count'], "")
                        return {"success": True, "message": generated_message}

        except Exception as error:
            logger.error(error)
            # Update status if status_object is not None
            if status_object is not None:
                status_object['Class'].change_status("ERROR_GENERATE_OPENAI_MESSAGE", status_object['try_count'], str(error))
            return {"success": False, "message": str(error)}

        # Update status if status_object is not None
        if status_object is not None:
            status_object['Class'].change_status("ERROR_GENERATE_OPENAI_MESSAGE", status_object['try_count'], "No message generated")
        return {"success": False, "message": "No message generated"}
    
class GenerateImage:

    USED_ORIGNAL_IMAGE_URL = []
    GENERATED_IMAGES = []
    KEYWORDS_WITH_ORIGINAL_URL = []

    @staticmethod
    def get_serp_images_valueserp_done(keyword_with_original_image_url):
        def callback(future):
            try:
                generated_image = future.result()
                keyword_with_original_image_url.append(generated_image)
                logger.info(f"Generated - {generated_image}")
            except TimeoutError as error:
                print("Function took longer than %d seconds" % error.args[1])
            except Exception as error:
                print("Function raised %s" % error)
                print(error.traceback)
        return callback

    @staticmethod
    def get_serp_images_valueserp(keyword, valueserp_api_key):
        logger.debug("get_serp_images_valueserp")
        return_images = []
        for try_count in range(0, 3):
            try:
                params = {
                    'api_key': valueserp_api_key,
                    'search_type': 'images',
                    'q': keyword,
                    'images_Size': 'large',
                    'google_domain': 'google.com',
                    'hl': 'en',
                    'filter': '0'
                }
                api_result = requests.get('https://api.valueserp.com/search', params)
                images_result = api_result.json()
                if not images_result['request_info']['success']:
                    logger.error(images_result)
                    return None
                images_result = images_result['image_results'][15:]
                random.shuffle(images_result)
                for image_data in images_result:
                    # if image_data['width'] < 700 or image_data['height'] < 500:
                    #     continue
                    return_images.append(image_data['image'])
                # logger.debug(images_result)
                # logger.debug(return_images)
                return {"keyword": keyword, "original_image_urls": return_images}
            except Exception as ex:
                logger.error(f"valueserp - try {try_count} - {ex}")
        return None

    @staticmethod
    def get_imagekit_urls(keyword, original_image_url):
        logger.debug("get_imagekit_urls")
        try: 
            # logger.debug(f"original_image_url: {original_image_url}")
            imagekit_url = GenerateImage.upload_image_to_imagekit(original_image_url, keyword)
            # logger.info(f"imagekit_url: {imagekit_url}")
            return imagekit_url
        except Exception as ex: 
            logger.error(ex)
        return None

    @staticmethod
    def upload_image_to_imagekit(image_url, keyword):
        logger.debug("upload_image_to_imagekit")
        try:
            imagekit = ImageKit(
                private_key=os.getenv("IMAGEKIT_PRIVATE_KEY", ""),
                public_key=os.getenv("IMAGEKIT_PUBLICK_KEY", ""),
                url_endpoint=os.getenv("IMAGEKIT_URL", "")
            )
            options = UploadFileRequestOptions(
                folder = datetime.datetime.now().strftime("%Y/%m/%d")
            )
            result = imagekit.upload_file(
                file=image_url, # required
                file_name=keyword+".jpg",
                options=options
            )
            return result.response_metadata.raw['url'] # Ignore this error in editor.
        except Exception as ex:
            logger.error(ex)
        return None

    @staticmethod
    def get_all_templates_by_tags(json_data, HasuraInline):
        try:
            # Get tags info
            tags = json_data['tags']
            column_data = [ { "column_name": "tag_name", "operator": "_in", "value": tags } ]
            tags_info = HasuraInline.get_by_columns_value_pair(TAGS_TABLE_INFO, column_data)
            if not tags_info['success']:
                logger.error("Didn't found tags")
                return {"success": False, "message": "Didn't found tags"}
            tags_info = tags_info['message']['data']['tags']
            if not tags_info:
                logger.error("Didn't found tags")
                return {"success": False, "message": "Didn't found tags"}
            
            # Get tags templates mapping info
            tag_ids = [tag_info['tag_id'] for tag_info in tags_info]
            column_data = [ { "column_name": "tag_id", "operator": "_in", "value": tag_ids } ]
            tags_templates_mapping_info = HasuraInline.get_by_columns_value_pair(TAGS_TEMPLATES_MAPPING_TABLE_INFO, column_data)
            tags_templates_mapping_info = tags_templates_mapping_info['message']['data']['tags_templates_mapping']

            # Get templates info
            template_ids = [ttmi['template_id'] for ttmi in tags_templates_mapping_info]
            column_data = [ { "column_name": "template_id", "operator": "_in", "value": template_ids } ]
            templates_info = HasuraInline.get_by_columns_value_pair(TEMPLATES_TABLE_INFO, column_data)
            return {"success": True, "message":templates_info['message']['data']['templates']}
        except Exception as ex:
            logger.error(ex)
            return {"success": False, "message": (ex)}

    @staticmethod
    def create_circular_templates_info(templates_info, number):
        # If templates_info doesn't have 5 elements, use circular array
        if len(templates_info) < number:
            templates_info = (templates_info * number)[:number]
        else:
            templates_info = templates_info[:number]
        # Shuffle templates_info
        random.shuffle(templates_info)
        return templates_info

    @staticmethod
    def create_circular_keywords(keywords, number):
        # If templates_info doesn't have 5 elements, use circular array
        if len(keywords) < number:
            keywords = (keywords * number)[:number]
        else:
            keywords = keywords[:number]
        # Shuffle templates_info
        return keywords

    @staticmethod
    def process_template_done(generated_images):
        def callback(future):
            try:
                generated_image = future.result()
                generated_images.append(generated_image)
                logger.info(f"Generated - {generated_image}")
            except TimeoutError as error:
                print("Function took longer than %d seconds" % error.args[1])
            except Exception as error:
                print("Function raised %s" % error)
                print(error.traceback)
        return callback

    @staticmethod
    def process_template(template, keyword_with_original_image_url, used_orignal_image_url):
        try:
            logger.debug("process_template")

            template_json = json.loads(template['template_json'])
            template_image_count = sum(1 for tj in template_json['objects'] if "layerImageCategory" in tj and tj['layerImageCategory'])
            template_text_count = sum(1 for tj in template_json['objects'] if "layerTextCategory" in tj and tj['layerTextCategory'])
            # logger.info(template_image_count)
            # logger.info(template_text_count)

            circular_keyword_with_original_image_url = GenerateImage.create_circular_keywords(keyword_with_original_image_url, template_image_count)
            imagekit_urls = []
            
            for ckwoiu in circular_keyword_with_original_image_url:
                keyword = ckwoiu['keyword']
                original_image_urls = ckwoiu['original_image_urls']
                for original_image_url in original_image_urls:
                    if original_image_url not in used_orignal_image_url:
                        used_orignal_image_url.append(original_image_url)
                        imagekit_url = GenerateImage.get_imagekit_urls(keyword, original_image_url)

                        # Check if the imagekit_url has an image using PIL
                        try:
                            response = requests.get(imagekit_url, stream=True)
                            response.raw.decode_content = True
                            image = Image.open(response.raw)
                            image_size_width = image.size[0]
                        except Exception as e:
                            logger.error(f"Failed to open image from url {imagekit_url}: {e}")
                            image = None

                        if image:
                            imagekit_urls.append(imagekit_url)
                            break

            try:
                counter = 0
                for obj in template_json['objects']:
                    if "layerImageCategory" in obj and obj['layerImageCategory']:
                        imagekit_url = imagekit_urls[counter]
                        width = round(obj['width'] * obj['scaleX'])
                        height = round(obj['height'] * obj['scaleY'])
                        imagekit_url = imagekit_url.rsplit("/", 1)[0] + \
                                        f"/tr:w-{width},h-{height},fo-auto" +  \
                                    "/" + imagekit_url.rsplit("/", 1)[1]
                        # logger.info(f"Modified imagekit : {imagekit_url}")
                        obj['width'] = width
                        obj['height'] = height
                        obj['scaleX'] = 1
                        obj['scaleY'] = 1
                        obj['src'] = imagekit_url
                        counter += 1
            except Exception as ex:
                logger.error(ex)

            # Generate templates.json file with random name in static/generated_json/ with content of templates variable
            file_name = "static/generated_json/" + str(random.randint(1000,9999)) + "_templates.json"
            # logger.debug(file_name)
            with open(file_name, 'w') as outfile:
                json.dump([template_json], outfile)
            # logger.debug(file_name)
            generated_image = GenerateImage.generate_image(file_name)
            return generated_image
        except Exception as ex:
            logger.error(ex)
        return None

    @staticmethod
    def generate_image(template_file_name):
        logger.debug(template_file_name)
        process = subprocess.Popen(["node", "generate_image.js", template_file_name], stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode()
        output = output.split()
        output = output[0]
        return output
