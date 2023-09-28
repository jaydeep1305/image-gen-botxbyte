(function($) {
    "use strict";
    // Dataurl to blob
    function dataURLtoBlob(dataurl) {
        var arr = dataurl.split(','), mime = 'image/png',
            bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], {type:mime});
    }
    var gj_canvas = '';
    $(document).ready(function () {
        /* Initialize Palleon plugin */
        $('#palleon').palleon({
            baseURL: "./", // The url of the main directory. For example; "http://www.mysite.com/palleon-js/"

            //////////////////////* CANVAS SETTINGS *//////////////////////
            fontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif", // Should be a web safe font
            fontSize: 60, // Default font size
            fontWeight: 'normal', // e.g. bold, normal, 400, 600, 800
            fontStyle: 'normal', // Possible values: "", "normal", "italic" or "oblique".
            canvasColor: 'transparent', // Canvas background color
            fill: '#000', // Default text color
            stroke: '#fff', // Default stroke color
            strokeWidth: 0, // Default stroke width
            textBackgroundColor: 'rgba(255,255,255,0)', // Default text background color
            textAlign: 'left', // Possible values: "", "left", "center" or "right". 
            lineHeight: 1.2, // Default line height.
            borderColor: '#000', // Color of controlling borders of an object (when it's active).
            borderDashArray: [4, 4], // Array specifying dash pattern of an object's borders (hasBorder must be true).
            borderOpacityWhenMoving: 0.5, // Opacity of object's controlling borders when object is active and moving.
            borderScaleFactor: 2, // Scale factor of object's controlling borders bigger number will make a thicker border border is 1, so this is basically a border thickness since there is no way to change the border itself.
            editingBorderColor: 'rgba(0,0,0,0.5)', // Editing object border color.
            cornerColor: '#fff', // Color of controlling corners of an object (when it's active).
            cornerSize: 12, // Size of object's controlling corners (in pixels).
            cornerStrokeColor: '#000', // Color of controlling corners of an object (when it's active and transparentCorners false).
            cornerStyle: 'circle', // Specify style of control, 'rect' or 'circle'.
            transparentCorners: false, // When true, object's controlling corners are rendered as transparent inside (i.e. stroke instead of fill).
            cursorColor: '#000', // Cursor color (Free drawing)
            cursorWidth: 2, // Cursor width (Free drawing)
            enableGLFiltering: true, // set false if you experience issues on image filters.
            textureSize: 4096, // Required for enableGLFiltering
            watermark: false, // true or false
            watermarkText: 'https://palleon.website/', // The watermark text
            watermarkFontFamily: 'Georgia, serif', // Should be a web safe font
            watermarkFontStyle: 'normal', // Possible values: "", "normal", "italic" or "oblique".
            watermarkFontColor: '#000', // Watermark font color
            watermarkFontSize: 40, // Watermark font size (integer only)
            watermarkFontWeight: 'bold', // e.g. bold, normal, 400, 600, 800
            watermarkBackgroundColor: '#FFF', // Watermark background color
            watermarkLocation: 'bottom-right', // Possible values: "bottom-right", "bottom-left", "top-left" and "top-right".
            layerTextCategory: '',
            layerImageCategory: '',

            //////////////////////* CUSTOM FUNCTIONS *//////////////////////
            customFunctions: function(selector, canvas, lazyLoadInstance) {
                /**
                 * @see http://fabricjs.com/fabric-intro-part-1#canvas
                 * You may need to update "lazyLoadInstance" if you are going to populate items of a grid with ajax. 
                 * lazyLoadInstance.update();
                 * @see https://github.com/verlok/vanilla-lazyload
                 */
                gj_canvas = canvas;
                /* Template - Add to Favorite */
                selector.find('.template-grid').on('click','.template-favorite button.star',function(){
                    var button = $(this);
                    var templateid = button.data('templateid');
                    
                    /* Do what you want */
                    
                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");
                });

                /* Frame - Add to Favorite */
                selector.find('.palleon-frames-grid').on('click','.frame-favorite button.star',function(){
                    var button = $(this);
                    var frameid = button.data('frameid');
                    
                    /* Do what you want */

                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");
                });

                /* Element - Add to Favorite */
                selector.find('.palleon-grid').on('click','.element-favorite button.star',function(){
                    var button = $(this);
                    var elementid = button.data('elementid');
                    
                    /* Do what you want */

                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");
                });

                /* Delete Template From Library */
                selector.find('.palleon-template-list').on('click','.palleon-template-delete',function(){
                    var answer = window.confirm("Are you sure you want to delete the template permanently?");
                    if (answer) {
                        var target = $(this).data('target');
                        $(this).parent().parent().remove();

                        /* Do what you want */

                        toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                        // toastr.error("Error!", "Lorem ipsum dolor");
                    }
                });

                /* Upload Image To Media Library */
                selector.find('#palleon-library-upload-img').on('change', function (e) {
                    var file_data = this.files[0];

                    /* Do what you want */

                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");
                });

                /* Delete Image From Media Library */
                selector.find('.media-library-grid').on('click','.palleon-library-delete',function(){
                    var answer = window.confirm("Are you sure you want to delete the image permanently?");
                    if (answer) {
                        var target = $(this).data('target');
                        $(this).parent().remove();

                        /* Do what you want */

                        toastr.success("Deleted!", "Lorem ipsum dolor");
                        // toastr.error("Error!", "Lorem ipsum dolor");
                    }
                });

                /* Upload SVG To Media Library */
                selector.find('#palleon-svg-library-upload-img').on('change', function (e) {
                    var file_data = this.files[0];

                    /* Do what you want */

                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");
                });

                /* Delete SVG From Media Library */
                selector.find('.svg-library-grid').on('click','.palleon-svg-library-delete',function(){
                    var answer = window.confirm("Are you sure you want to delete the image permanently?");
                    if (answer) {
                        var target = $(this).data('target');
                        $(this).parent().remove();

                        /* Do what you want */

                        toastr.success("Deleted!", "Lorem ipsum dolor");
                        // toastr.error("Error!", "Lorem ipsum dolor");
                    }
                });

                // Save preferences
                selector.find('#palleon-preferences-save').on('click', function() {
                    var button = $(this);
                    var settings = {};
                    var keys = [];
                    var values = [];
                    selector.find('#palleon-preferences .preference').each(function(index, value) {
                        keys.push($(this).attr('id'));
                        values.push($(this).val());
                    });

                    for (let i = 0; i < keys.length; i++) {
                        settings[keys[i]] = values[i];
                    }

                    var preferences = JSON.stringify(settings);

                    /* Do what you want */

                    toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                    // toastr.error("Error!", "Lorem ipsum dolor");

                });

            },

            //////////////////////* SAVE TEMPLATE *//////////////////////
            saveTemplate: function(selector, template) {
                /**
                 * var template is JSON string
                 * @see http://fabricjs.com/docs/fabric.Canvas.html#toDataURL
                 */
                var template_name = $("#palleon-json-save-name").val();
                if(!template_name.trim()){
                    alert("Enter File Name.");
                    return;
                }
                var imageTags = selector.find('#palleon-adjust #palleon-image-tags').val();
                if(!imageTags.length){
                    alert("Image Tags are required.");
                    return;
                }
                
                template = JSON.parse(template);
                // Layer Category
                template.objects.forEach(function(object) {    
                    if(object.type === 'textbox') {
                        
                        var maxLength, minLength;                        
                        switch(object.layerTextCategory) {
                            case "headline": maxLength = 30; minLength = 10; break;
                            case "sub_headline": maxLength = 50; minLength = 20; break;
                            case "category": maxLength = 15; minLength = 5; break;
                            case "author_name": maxLength = 15; minLength = 5; break;
                            case "author_job_post": maxLength = 15; minLength = 5; break;
                            default: maxLength = 0; minLength = 0; break;
                        }

                        template.objects[template.objects.indexOf(object)].maxLength = maxLength;
                        template.objects[template.objects.indexOf(object)].minLength = minLength;
                    }
                    if(object.type === 'image'){
                        console.log(object.layerImageCategory);
                    }
                    /*-- Confuse regarding uuid
                    // Generate UUID
                    function generateUUID() { // Public Domain/MIT
                        var d = new Date().getTime();//Timestamp
                        var d2 = (performance && performance.now && (performance.now()*1000)) || 0;//Time in microseconds since page-load or 0 if unsupported
                        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                            var r = Math.random() * 16;//random number between 0 and 16
                            if(d > 0){//Use timestamp until depleted
                                r = (d + r)%16 | 0;
                                d = Math.floor(d/16);
                            } else {//Use microseconds since page-load if supported
                                r = (d2 + r)%16 | 0;
                                d2 = Math.floor(d2/16);
                            }
                            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                        });
                    }
                    object['uuid'] = object['uuid'] ? object['uuid'] : generateUUID();
                    ---*/
                });
                
                // Image Tags
                template['imageTags'] = imageTags;
                
                var template_width = template.backgroundImage.width;
                var template_height = template.backgroundImage.height;

                template = JSON.stringify(template);
                console.log(template);
                

                /*-- 
                    Generate Image from Template to upload
                --*/
                // Reinitialize the existing canvas instead of creating a new one
                var imgData = gj_canvas.toDataURL({ format: "png", quality: "100", enableRetinaScaling: false});

                var send_data = {"imgData": imgData, "template_name": template_name}
                $.ajax({
                    url: '/upload-image',
                    type: 'POST',
                    data: JSON.stringify(send_data),
                    contentType: 'application/json',
                    success: function(data) {
                        var template_image_path = data.trim();

                        var json_data = {};
                        json_data['template_name'] = template_name;
                        json_data['template_json'] = template;
                        json_data['image_tags'] = imageTags;
                        json_data['template_width'] = template_width;
                        json_data['template_height'] = template_height;
                        json_data['template_image_path'] = template_image_path;
                        
                        $.ajax({
                            type: "POST",
                            url: "/save",
                            data: JSON.stringify(json_data),
                            contentType: "application/json",
                            success: function(response) {
                                console.log(response);
                                toastr.success(response.responseText, "Saved.");
                            },
                            error: function(error) {
                                console.log(error);
                                toastr.error(error.responseText, "Error in saving.");
                            }
                        });
                    },
                    error: function(error) {
                        console.log('Error in uploading image:\n' + error);
                    }
                });
                
            },

            //////////////////////* SAVE IMAGE *//////////////////////
            saveImage: function(selector, imgData) {
                var name = selector.find('#palleon-save-img-name').val();
                var quality = parseFloat(selector.find('#palleon-save-img-quality').val());
                var format = selector.find('#palleon-save-img-format').val();

                if (format == 'svg') {
                    // var imgData is raw svg code
                    console.log(imgData);

                    /* Do what you want */
                } else {
                    /**
                     * var imgData is DataURL
                     * @see https://flaviocopes.com/data-urls/
                     * @see http://fabricjs.com/docs/fabric.Canvas.html#toDataURL
                     */
                    console.log(imgData);

                    /* Do what you want */
                }

                toastr.success("To make 'saving functions' work, you should have a database on your server and integrate it to Palleon using a server-side language. See Documentation -> Integration.", "Info");
                // toastr.error("Error!", "Lorem ipsum dolor");
            }
        });
    });

})(jQuery);