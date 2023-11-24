from flask import Flask, render_template, request
import cv2
import cvlib as cv
import numpy as np

app = Flask(__name__)

def find_density(images):
    results = {}
    
    for i, image in enumerate(images, start=1):
        bbox, label, conf = cv.detect_common_objects(image)
        total = label.count('person') + label.count('car') + label.count('motorcycle') + label.count('truck')
        print(f'Number of vehicles in cam-{i} in the image is {total}')
        results[f'lane-{i}'] = total

    sorted_density = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return sorted_density

def check_density(images):
    sorted_density = find_density(images)
    maxx = 10
    traffic_light_data = []

    for i in sorted_density:
        lane = i[0]
        if i[1] == 0:
            traffic_light_data.append((lane, 11))
        elif i[1] > maxx:
            traffic_light_data.append((lane, 36))
        else:
            traffic_light_data.append((lane, 26))

    return traffic_light_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        images = []
        for i in range(1, 5):
            file_key = f'image{i}'
            if file_key not in request.files:
                return render_template('index.html', error='Please upload all four images.')

            file = request.files[file_key]

            if file.filename == '':
                return render_template('index.html', error='Please select all four images.')

            img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), -1)
            images.append(img)

        traffic_light_data = check_density(images)
        return render_template('result.html', traffic_light_data=traffic_light_data)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
