from flask import Flask, request, render_template
import requests
from PIL import Image
import io
import base64

app = Flask(__name__)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['file']
    if file:
        image = Image.open(file.stream)
        plant_name = detect_leaf(image)
        details = fetch_wikipedia_details(plant_name)
        quality = assess_plant_quality(image)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return render_template('result.html', plant_name=plant_name, details=details, quality=quality, img_base64=img_base64)

def detect_leaf(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

    # Plant.id API
    api_url = 'https://api.plant.id/v2/identify'
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': 'ivtI1GfCicjnR0evapVb5r7HbsqquccWmLBkGa3UsfhupnGgvg' 
    }
    data = {
        "images": [img_base64],
        "organs": ["leaf"]
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()
    
    if result['suggestions']:
        return result['suggestions'][0]['plant_name']
    else:
        return "Unknown Plant"

def fetch_wikipedia_details(plant_name):
    # Fetch details from Wikipedia
    formatted_name = plant_name.replace(" ", "_")  
    response = requests.get(f'https://en.wikipedia.org/w/api.php?action=query&format=json&titles={formatted_name}&prop=extracts&exintro=&explaintext=&redirects=1')
    data = response.json()
    page = next(iter(data['query']['pages'].values()))
    return page.get('extract', 'No information found.')

def assess_plant_quality(image):
    
    brightness = image.convert('L').point(lambda x: x > 128 and 255)  # Simple threshold for brightness
    if brightness.getextrema()[1] > 128:  # If the max brightness is above 128
        return "Healthy"
    else:
        return "Rusty"

if __name__ == '__main__':
    app.run(debug=True)