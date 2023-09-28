import { fabric } from 'fabric'
import fs from 'fs'
import ImageKit from "imagekit";
import dotenv from 'dotenv';
dotenv.config();

var imagekit = new ImageKit({
    publicKey: process.env.IMAGEKIT_PUBLICK_KEY,
    privateKey: process.env.IMAGEKIT_PRIVATE_KEY,
    urlEndpoint: process.env.IMAGEKIT_URL
});


(() => {
    let json_data = fs.readFileSync(process.argv[2], 'utf8');
    json_data = JSON.parse(json_data)

    for (const template of json_data) {
        const canvas = new fabric.Canvas(null, { width: template.backgroundImage.width, height: template.backgroundImage.height });
        const objects = JSON.stringify(template);
        canvas.loadFromJSON(objects, function () {
            canvas.renderAll();
            const imageData = canvas.toDataURL();

            uploadFile(imageData).then(res => console.log(res.url)).catch(e => console.log(e.message))
        });

    }
})()

async function uploadFile(image, filename = `img.png`) {
    return new Promise((resolve, reject) => {

        return imagekit.upload({
            file: image,
            fileName: filename
        }, function (error, result) {
            if (error) reject(error);

            return resolve(result)
        })

    })
}




