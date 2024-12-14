from django.shortcuts import render
import json
import os

def dashboard(request):
    raw = 'analysis/templates/analysis/raw_signals/'
    content = {'raw': [], 'fft': [], 'bearing_analysis_results': {}, 'filtered_signals': [], 'prediction_analysis': {},}
    for f in os.listdir(raw):
        content['raw'].append(f)

    fft = 'analysis/templates/analysis/fft_analysis/'
    for f in os.listdir(fft):
        content['fft'].append(f)

    with open('analysis/static/analysis/data/bearing_analysis_results.json', 'r') as file:
        bearing_analysis_results = json.load(file)
        content['bearing_analysis_results'] = bearing_analysis_results

    filtered_signals = 'analysis/templates/analysis/filtered_signals/'
    for f in os.listdir(filtered_signals):
        content['filtered_signals'].append(f)

    with open('analysis/static/analysis/data/prediction_analysis.json', 'r') as file:
        prediction_analysis = json.load(file)
        content['prediction_analysis'] = prediction_analysis

    return render(request, 'analysis/dashboard.html', {'content': content})