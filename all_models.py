TEMPLATES_TABLE_INFO = {
    "table": "templates",
    "constraint": "templates_template_name_key",
    "order_by": {
        "column": "updated_at",
        "order": "desc"
    },
    "editable": True,
    "columns": [
        {
            "name": "template_name",
            "label": "Template Name",
            "placeholder": "Template Name",
            "type": "text_input",
            "required": True,
            "hide_column": False
        },
        {
            "name": "template_json",
            "label": "Template Json",
            "placeholder": "Template Json",
            "type": "text_area",
            "required": True,
            "hide_column": False
        },
        {
            "name": "template_image_path",
            "label": "Template Image Path",
            "placeholder": "Template Image Path",
            "type": "text_area",
            "required": True,
            "hide_column": False
        },
        {
            "name": "status",
            "label": "Status",
            "placeholder": "Status",
            "type": "selectbox",
            "required": True,
            "hide_column": False,
            "options": [
                "ACTIVE",
                "SUSPEND"
            ]
        },
        {
            "name": "template_id",
            "label": "Template Id",
            "placeholder": "Template Id",
            "type": "text_input",
            "required": False,
            "hide_column": False,
            "update": False,
            "auto_generate": True,
            "primary_key": "True"
        }
    ]
}
TAGS_TABLE_INFO = {
    "table": "tags",
    "constraint": "tags_tag_name_key",
    "order_by": {
        "column": "updated_at",
        "order": "desc"
    },
    "editable": True,
    "columns": [
        {
            "name": "tag_name",
            "label": "Tag Name",
            "placeholder": "Tag Name",
            "type": "text_input",
            "required": True,
            "hide_column": False
        },
        {
            "name": "status",
            "label": "Status",
            "placeholder": "Status",
            "type": "selectbox",
            "required": True,
            "hide_column": False,
            "options": [
                "ACTIVE",
                "SUSPEND"
            ]
        },
        {
            "name": "tag_id",
            "label": "Tag Id",
            "placeholder": "Tag Id",
            "type": "text_input",
            "required": False,
            "hide_column": False,
            "auto_generate": True,
            "update": False,
            "primary_key": "True"
        }
    ]
}
TAGS_TEMPLATES_MAPPING_TABLE_INFO = {
    "table": "tags_templates_mapping",
    "constraint": "tags_templates_mapping_tag_id_template_id_key",
    "order_by": {
        "column": "tags_templates_mapping_id",
        "order": "desc"
    },
    "editable": True,
    "columns": [
        {
            "name": "tag_id",
            "label": "Tag Id",
            "placeholder": "Tag Id",
            "type": "text_input",
            "required": True,
            "hide_column": False
        },
        {
            "name": "template_id",
            "label": "Template Id",
            "placeholder": "Template Id",
            "type": "text_input",
            "required": True,
            "hide_column": False
        },
        {
            "name": "tags_templates_mapping_id",
            "label": "Tag Templates Mapping Id",
            "placeholder": "Tag Templates Mapping Id",
            "type": "text_input",
            "required": False,
            "hide_column": False,
            "auto_generate": True,
            "update": False,
            "primary_key": "True"
        }
    ]
}
