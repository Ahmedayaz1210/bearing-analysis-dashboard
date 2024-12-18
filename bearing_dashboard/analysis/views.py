from django.shortcuts import render
import json
import os

def dashboard(request):
    content = {'raw': [], 'fft': [], 'bearing_analysis_results': {}, 'filtered_signals': [], 'prediction_analysis': {},}

    raw = 'analysis/templates/analysis/raw_signals/'
    content['raw'] = []

    # List files in the raw_signals directory
    raw_files = os.listdir(raw)

    if not raw_files:  # If no files are found
        content['raw'] = [{'error': 'No raw signals found'}]
    else:
        for f in raw_files:
            content['raw'].append(f)

        

    fft = 'analysis/templates/analysis/fft_analysis/'
    for f in os.listdir(fft):
        content['fft'].append(f)

    try:
        with open('analysis/static/analysis/data/bearing_analysis_results.json', 'r') as file:
            bearing_analysis_results = json.load(file)
            content['bearing_analysis_results'] = bearing_analysis_results
    except PermissionError as e:
        content['bearing_analysis_results'] = {'error': 'Error accessing bearing analysis data'}
    except Exception as e:
        content['bearing_analysis_results'] = {'error': 'An error occurred while loading bearing analysis data'}




    filtered_signals = 'analysis/templates/analysis/filtered_signals/'
    for f in os.listdir(filtered_signals):
        content['filtered_signals'].append(f)

    with open('analysis/static/analysis/data/prediction_analysis.json', 'r') as file:
        prediction_analysis = json.load(file)
        if 'model_performance' in prediction_analysis:
            model_perf = prediction_analysis['model_performance']
            if 'average_accuracy' in model_perf:
                if model_perf['average_accuracy'] < 0 or model_perf['average_accuracy'] > 100:
                    model_perf['error_message'] = 'Invalid average accuracy percentage'
        
        content['prediction_analysis'] = prediction_analysis

    return render(request, 'analysis/dashboard.html', {'content': content})