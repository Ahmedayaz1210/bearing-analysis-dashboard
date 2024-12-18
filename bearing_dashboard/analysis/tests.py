from django.test import TestCase

import pytest
import os
import json
from bs4 import BeautifulSoup
import builtins

# 1. Tests basic view response and status code
@pytest.mark.django_db            
def test_view(client):            
    url = ""  
    response = client.get(url)     
    assert response.status_code == 200  

# 2. Tests if the required directories and files exist
def test_required_plots_exist():
    assert os.path.exists(os.path.join('analysis', 'static', 'analysis', 'images', 'feature_correlation_matrix.png')), "Missing correlation matrix plot"


# 3. Tests dashboard error handling for invalid accuracy values
@pytest.mark.django_db
def test_dashboard_error_handling(client, monkeypatch):
    data_dir = os.path.join('analysis', 'static', 'analysis', 'data')
    prediction_path = os.path.join(data_dir, 'prediction_analysis.json')
    
    with open(prediction_path, 'r') as f:
        prediction_analysis = json.load(f)

    def mock_load_prediction_data(*args, **kwargs):
        modified_data = prediction_analysis.copy()
        for mp_bp, mp_bp_data in modified_data.items():
            for key, value in mp_bp_data.items():
                if key == 'average_accuracy':
                    mp_bp_data[key] = -100
        return modified_data
    
    monkeypatch.setattr('json.load', mock_load_prediction_data)

    response = client.get('')
    content = response.content.decode('utf-8')

    assert response.status_code == 200

    assert 'Invalid average accuracy percentage' in content, "Missing error message for invalid accuracy percentage"
    

# 4. Tests file system permission error handling
@pytest.mark.django_db
def test_file_system_permission_error(client, monkeypatch):
    """
    Test how dashboard handles file permission errors when reading JSON data
    """
    original_open = builtins.open
    def mock_file_open(*args, **kwargs):
        if 'bearing_analysis_results.json' in args[0]:
            raise PermissionError("Permission denied: bearing_analysis_results.json")
        return original_open(*args, **kwargs)

    monkeypatch.setattr('builtins.open', mock_file_open)

    response = client.get('')
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'Error accessing bearing analysis data' in content, "Missing error message for file access error"

# 5. Tests handling of missing plot files
@pytest.mark.django_db
def test_missing_plot_files_error(client, monkeypatch):
    """
    Test how dashboard handles missing plot files
    """
    original_listdir = os.listdir
    def mock_listdir(path):
        if 'raw_signals' in path:
            return []
        return original_listdir(path)

    monkeypatch.setattr('os.listdir', mock_listdir)

    response = client.get('')
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'No raw signals found' in content, "Missing error message for missing raw signal files"


# 6. Fixture providing JSON file paths
@pytest.fixture
def json_file_paths():
    data_dir = os.path.join('analysis', 'static', 'analysis', 'data')
    return {
        'prediction': os.path.join(data_dir, 'prediction_analysis.json'),
        'bearing': os.path.join(data_dir, 'bearing_analysis_results.json')
    }

# 7. Fixture loading prediction analysis data
@pytest.fixture
def prediction_analysis(json_file_paths):
    with open(json_file_paths['prediction'], 'r') as f:
        return json.load(f)

# 8. Tests prediction analysis JSON content structure
def test_prediction_analysis_content(prediction_analysis):

    assert len(prediction_analysis) > 0, "File is empty"

    for mp_bp, mp_bp_data in prediction_analysis.items():
        assert mp_bp in ['model_performance', 'bearing_predictions'], f"Invalid key: {mp_bp}"
        assert len(mp_bp_data) > 0, f"Empty data for {mp_bp}"
        for key, value in mp_bp_data.items():
            if mp_bp == 'model_performance':
                assert key in ['average_accuracy', 'average_error_days'], f"Invalid key: {key}"
                assert value >= 0, f"Error can't be negative: {value}"
                if key == 'average_accuracy':
                    assert value < 100, f"Accuracy can't go above 100%: {value}"
            else:
                assert len(value) > 0, f"Empty data for {key}"
                assert 'Set' and 'Bearing' in key, f"Expected a set and a bearing number in {mp_bp} but got: {key}"
                for set_and_bearing, set_and_bearing_data in value.items():
                    if set_and_bearing == 'average_accuracy':
                        assert set_and_bearing_data < 100, f"Accuracy can't go above 100%: {set_and_bearing_data}"
                    else:
                        for time_data in set_and_bearing_data:
                            for life_and_predictions, life_and_predictions_data in time_data.items():
                                assert life_and_predictions in ['life_stage', 'predictions'], f"Expected Life stage and predictions, got: {life_and_predictions}"
                                assert len(life_and_predictions_data) > 0, f"Empty data for {life_and_predictions}"

                                if life_and_predictions == 'life_stage':
                                    any_percentage = any(f"{pct}%" in life_and_predictions_data for pct in ["25", "50", "75", "90"])
                                    assert any_percentage, f"Expected one of 25%, 50%, 75%, or 90%, got: {life_and_predictions_data}"

                                else :
                                    for prediction, prediction_data in life_and_predictions_data.items():
                                        assert prediction in ["actual_hours_remaining", "predicted_hours", "error_metrics"], f"Expected actual_hours_remaining, predicted_hours, or error_metrics, got: {prediction}"


# 9. Fixture loading bearing analysis data  
@pytest.fixture
def bearing_analysis(json_file_paths):
    with open(json_file_paths['bearing'], 'r') as f:
        return json.load(f)

# 10. Tests bearing analysis results content structure
def test_bearing_analysis_result_content(bearing_analysis):
    
    assert len(bearing_analysis) > 0, "File is empty"
    assert all(f"set {i}" in bearing_analysis for i in [1, 2, 3]), "Missing required sets"
    
    expected_structure = {
        "set 1": ["bearing 3", "bearing 4"],
        "set 2": ["bearing 1"],
        "set 3": ["bearing 3"]
    }
    
    for set_name, bearings in bearing_analysis.items():
        assert set_name in expected_structure, f"Unexpected set: {set_name}"
        
        for bearing_name, bearing_data in bearings.items():
            assert bearing_name in expected_structure[set_name], f"Unexpected bearing {bearing_name} in {set_name}"
            
            assert 0 <= bearing_data['failure_point_percentage'] <= 100, f"Invalid failure percentage: {bearing_data['failure_point_percentage']}"
            
            for channel_name, channel_data in bearing_data['channels'].items():
                changes = channel_data['changes']
                
                for metric, value in changes['magnitude'].items():
                    assert metric in ['peak', 'mean', 'total_energy'], f"Invalid magnitude metric: {metric}"
                    assert isinstance(value, (int, float)), f"Non-numeric value in magnitude: {value}"
                    assert value >= 0, f"Negative magnitude value: {value}"
                
                bands = changes['frequency_bands']
                expected_bands = ['low_band_change', 'mid_band_change', 'high_band_change']
                for band in expected_bands:
                    assert band in bands, f"Missing frequency band: {band}"
                    assert isinstance(bands[band], (int, float)), f"Non-numeric frequency band value: {bands[band]}"
                    assert bands[band] >= 0, f"Negative frequency band value: {bands[band]}"    



# 11. Tests prediction degradation patterns
def test_bearing_failure_signatures(bearing_analysis):
    
    # Inner Race Failure Analysis (Set 1, Bearing 3)
    inner_race = bearing_analysis['set 1']['bearing 3']
    inner_race_channels = inner_race['channels']
    
    # Inner race failures should show strongest high-frequency response
    for channel in inner_race_channels.values():
        freq_bands = channel['changes']['frequency_bands']
        assert freq_bands['high_band_change'] > freq_bands['mid_band_change'], \
            "Inner race failure signature violated: High frequency should dominate"
        
        # Verify cross-channel correlation (matched pairs)
        ch5_to_ch6_ratio = inner_race_channels['channel 5']['changes']['magnitude']['mean'] / \
                          inner_race_channels['channel 6']['changes']['magnitude']['mean']
        assert 0.8 <= ch5_to_ch6_ratio <= 1.2, \
            "Inner race channels should show balanced degradation"

    # Roller Element Analysis (Set 1, Bearing 4)
    roller = bearing_analysis['set 1']['bearing 4']
    roller_channels = roller['channels']
    
    # Roller failures show distinctive mid-frequency dominance
    for channel in roller_channels.values():
        freq_bands = channel['changes']['frequency_bands']
        assert freq_bands['mid_band_change'] > freq_bands['low_band_change'], \
            "Roller element signature violation: Mid-frequency should lead"
        
        # Early detection characteristic
        assert roller['failure_point_percentage'] < 85, \
            "Roller element failures should show earlier detection patterns"

    # Outer Race Analysis (Sets 2 and 3)
    outer_races = {
        'set 2': bearing_analysis['set 2']['bearing 1'],
        'set 3': bearing_analysis['set 3']['bearing 3']
    }
    
    for set_name, outer_race in outer_races.items():
        channel_data = list(outer_race['channels'].values())[0]
        freq_bands = channel_data['changes']['frequency_bands']
        
        # Outer race shows more uniform frequency distribution
        max_band = max(freq_bands.values())
        min_band = min(freq_bands.values())
        band_ratio = min_band / max_band if max_band != 0 else 0
        
        assert band_ratio > 0.4, \
            f"Outer race failure in {set_name} shows unexpected frequency distribution"
        


# 12. Tests prediction degradation patterns
def test_prediction_degradation_patterns(prediction_analysis):
    

    predictions = prediction_analysis['bearing_predictions']
    
    for bearing_type, bearing_data in predictions.items():
        timeline = bearing_data['timeline']
        
        # Analyze prediction accuracy degradation
        accuracies = [stage['predictions']['error_metrics']['accuracy_percentage'] 
                     for stage in timeline]
        
        # Early stage predictions should be more accurate
        assert accuracies[0] > accuracies[-1], \
            f"{bearing_type}: Early predictions should be more accurate than late-stage"
        
        # Check for realistic degradation patterns
        hours_remaining = [stage['predictions']['actual_hours_remaining'] 
                         for stage in timeline]
        
        
        # Special handling for different failure modes
        if "Inner Race" in bearing_type:
            # Inner race should show rapid accuracy decline near failure
            late_stage_drop = accuracies[-2] - accuracies[-1]
            assert late_stage_drop > 30, \
                "Inner race should show characteristic rapid decline"
                
        elif "Roller Element" in bearing_type:
            # Roller element should maintain better late-stage accuracy
            assert accuracies[-1] > 70, \
                "Roller element should maintain prediction accuracy"
                
        elif "Outer Race" in bearing_type:
            # Check for characteristic plateau in mid-life
            mid_accuracies = accuracies[1:3]
            accuracy_variation = max(mid_accuracies) - min(mid_accuracies)
            assert accuracy_variation < 15, \
                "Outer race should show stable mid-life predictions"


# 13. Tests section IDs and titles in template
@pytest.mark.django_db
@pytest.mark.parametrize("section_id, expected_title", [
    ("Raw_Signals_Plots", "Raw Channel Signals - Failing Bearings"),
    ("Frequency_Domain_Analysis_Plots", "Frequency Domain Analysis (FFT)"),
    ("Frequency_Domain_Analysis_Result", "FFT Analysis Results"),
    ("filtered_signals_plots", "Filtered Signal Analysis"),
    ("degradation_analysis", "Degradation Analysis Over Time"),
    ("correlation_matrix_png", "Feature Correlation Matrix"),
    ("prediction_analysis_result", "Failure Prediction Analysis"),
    ("prediction_plots", "Prediction Plots"),
])
def test_section_ids(client, section_id, expected_title):
    response = client.get('')
    content = response.content.decode('utf-8')
    scrape = BeautifulSoup(content, 'html.parser')
    section = scrape.find('h2', {'id': section_id})
    assert section, f"Missing section with ID: {section_id}"
    assert section.text.strip() == expected_title, f"Wrong title for {section_id}. Expected '{expected_title}' but got '{section.text.strip()}'"


# 14. Tests template rendering and structure
@pytest.mark.django_db
def test_template_rendering(client):
    response = client.get('')
    assert response.status_code == 200

    content = response.content.decode('utf-8')
    
    assert 'Vibration Analysis Dashboard' in content, "Missing Vibration Analysis Dashboard title"

    scrape = BeautifulSoup(content, 'html.parser')

    prediction_elements = scrape.find('div', class_='prediction-container')
    performance = prediction_elements.find('div', class_='performance-summary')
    assert performance, "Missing performance summary"
    assert performance.find('span', class_='stat-label', string='Average Accuracy:'), "Missing accuracy label"
    assert performance.find('span', class_='stat-label', string='Average Error:'), "Missing error label"

    bearing_containers = scrape.find_all('div', class_='bearing-container')
    assert bearing_containers, "Missing bearing data containers"
    
    fft_results = scrape.find('div', class_='json-container')
    assert fft_results, "Missing FFT analysis results"
    assert fft_results.find_all('div', class_='set-container'), "Missing bearing set containers"

    tables = scrape.find_all('table', class_='prediction-table')
    assert tables, "Missing prediction tables"
    for table in tables:
        headers = table.find_all('th')
        required_headers = ['Life Stage', 'Actual Hours', 'Predicted Hours', 'Error (Hours)', 
                          'Error (Days)', 'Accuracy (%)']
        for header in required_headers:
            assert any(h.text.strip() == header for h in headers), f"Missing table header: {header}"


# 15. Tests required sections exist in context
@pytest.mark.django_db
@pytest.mark.parametrize("required_section", [
    'raw', 
     'fft', 
     'filtered_signals', 
     'bearing_analysis_results', 
     'prediction_analysis',
])
def test_required_sections_exist(client, required_section):
    response = client.get('')
    context = response.context
    content = context['content']

    assert required_section in content, f"Missing required section: {required_section}"


# 16. Tests view context data processing and validation
@pytest.mark.django_db
def test_view_context_data(client):
    # Get the response and extract context
    response = client.get('')
    context = response.context
    
    # Verify we have our main content container
    assert 'content' in context, "Missing content in context"
    content = context['content']


    # Test Bearing Analysis Results processing
    bearing_results = content['bearing_analysis_results']
    
    # Verify Set 1 Inner Race processing
    inner_race = bearing_results['set 1']['bearing 3']
    assert inner_race['failure_point_percentage'] > 99, "Inner race failure point incorrectly processed"
    
    # Check channel processing for paired sensors
    ch5 = inner_race['channels']['channel 5']
    ch6 = inner_race['channels']['channel 6']
    
    # Verify frequency band relationships maintained
    assert ch5['changes']['frequency_bands']['high_band_change'] > \
           ch5['changes']['frequency_bands']['low_band_change'], \
           "Frequency band relationship lost in processing"
    
    # Test energy calculations preserved
    assert abs(ch5['changes']['magnitude']['mean'] - 
              ch5['changes']['magnitude']['total_energy']) < 0.001, \
              "Energy calculations modified during processing"

    # Test Prediction Analysis processing
    predictions = content['prediction_analysis']
    
    # Verify model performance metrics
    model_perf = predictions['model_performance']
    assert 0 <= model_perf['average_accuracy'] <= 100, "Invalid accuracy range"
    assert model_perf['average_error_days'] >= 0, "Negative error days"

    # Test timeline processing for each bearing
    for bearing_name, bearing_data in predictions['bearing_predictions'].items():
        # Check life stages are properly ordered
        timeline = bearing_data['timeline']
        life_stages = [stage['life_stage'] for stage in timeline]
        expected_stages = ['25% through life', '50% through life', 
                         '75% through life', '90% through life']
        assert life_stages == expected_stages, f"Incorrect life stage ordering for {bearing_name}"
        
        # Verify predictions maintain physical consistency
        hours_remaining = [stage['predictions']['actual_hours_remaining'] 
                         for stage in timeline]
        assert all(hours_remaining[i] > hours_remaining[i+1] 
                  for i in range(len(hours_remaining)-1)), \
                  f"Hours remaining not monotonically decreasing for {bearing_name}"
        
        # Check accuracy calculations preserved
        for stage in timeline:
            pred = stage['predictions']
            # Verify accuracy calculation matches hours difference
            calculated_accuracy = 100 * (1 - abs(pred['actual_hours_remaining'] - 
                                               pred['predicted_hours']) / 
                                           pred['actual_hours_remaining'])
            assert abs(calculated_accuracy - 
                      pred['error_metrics']['accuracy_percentage']) < 0.3, \
                      f"Accuracy calculation modified for {bearing_name}"

    # Test plot data preparation
    assert all(plot.endswith('.html') for plot in content['raw']), \
           "Raw signal plots incorrectly formatted"
    assert all(plot.endswith('.html') for plot in content['fft']), \
           "FFT plots incorrectly formatted"