
    @staticmethod
    def depricated_process_template(template, json_data):
        try:
            logger.debug("process_template")
            template_json = json.loads(template['template_json'])
            template_image_count = sum(1 for tj in template_json['objects'] if "layerImageCategory" in tj and tj['layerImageCategory'])
            template_text_count = sum(1 for tj in template_json['objects'] if "layerTextCategory" in tj and tj['layerTextCategory'])

            keyword_or_title = json_data['keyword_or_title']
            logger.info(template_image_count)
            logger.info(template_text_count)

            keywords = []
            generated_texts = []

            # ai is not using at this time.
            ai_flag = False
            if ai_flag:
                # keyword_or_title to serp keyword generation for Image
                for try_count in range(0, 5):
                    try:
                        messages = [
                            {"role": "system", "content": ""},
                            {
                                "role": "assistant",
                                "content": f"""Generate {template_image_count} relevant Google search keywords based on the given title '{keyword_or_title}'. These keywords should be suitable for retrieving high-quality images related to the title's topic. The goal is to provide keywords that would yield the best image search results, showcasing various aspects of exhaust fans in the year 2023. Ensure that the generated keywords are specific and pertinent to the subject matter. Please list the {template_image_count} keywords separately, ensuring they are related to the title and would help in finding images that match the context. output: {{ "keywords": ["keyword1", "keyword2", "keyword3"] }}"""
                            }
                        ]
                        generated_message = PromptServiceInline.generate_openai_message(messages)
                        if generated_message['success']:
                            generated_message = generated_message['message']
                            logger.debug(generated_message)
                            generated_message = json.loads(generated_message)
                            keywords = generated_message['keywords']
                            logger.debug(f"Generated keywords : {json.dumps(keywords)}")
                            break
                    except Exception as ex:
                        logger.error(f"try-count : {try_count} Title to SERP Keyword Generation  - {ex}")
            else:
                keywords = [keyword_or_title]
    
            if not keywords:
                logger.error("SERP Error")
                return {"success": False, "message": "Serp Error"}
            
            keyword_imagekit_urls = []
            for keyword in keywords:
                json_data['keyword_or_title'] = keyword
                imagekit_url = GenerateImage.get_imagekit_urls(json_data)
                # Merge the imagekit_url into the keyword_imagekit_urls array
                keyword_imagekit_urls += imagekit_url
                logger.debug(keyword_imagekit_urls)
            
            try:
                for obj in template_json['objects']:
                    if "layerImageCategory" in obj and obj['layerImageCategory']:
                        obj['src'] = random.choice(keyword_imagekit_urls)
            except Exception as ex:
                logger.error(ex)

            # Generate templates.json file with random name in static/generated_json/ with content of templates variable
            file_name = "static/generated_json/" + str(random.randint(1000,9999)) + "_templates.json"
            logger.debug(file_name)
            with open(file_name, 'w') as outfile:
                json.dump([template_json], outfile)
            logger.debug(file_name)
            
            return file_name
        except Exception as ex:
            logger.error(ex)
        return None
