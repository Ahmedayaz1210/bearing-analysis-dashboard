# Bearing Analysis Dashboard

A web-based visualization system for industrial bearing health monitoring, built on Django and AWS infrastructure. This dashboard transforms complex vibration analysis data into actionable insights through interactive visualizations and real-time monitoring capabilities.

[![Dashboard](https://img.shields.io/badge/Visit-Dashboard-blue?style=for-the-badge&logo=amazonwebservices)](http://vibrationanalysislb-527968510.us-east-1.elb.amazonaws.com:8000/)

## Analysis Repository
The underlying analysis system that powers this dashboard's visualizations and predictions can be found here:
[![Analysis Repository](https://img.shields.io/badge/View_Analysis_Code-red?style=for-the-badge&logo=github)](https://github.com/Ahmedayaz1210/Vibration-Analysis-System)

## Technical Implementation

### Data Visualization Architecture

The dashboard implements a multi-layered visualization approach for bearing health monitoring:

1. **Raw Signal Visualization Layer**
   - Interactive time-domain plots showing vibration amplitude evolution
   - Real-time signal processing with Plotly for dynamic updating

2. **Frequency Analysis Layer**
   - FFT transformation visualizations across three critical bands:
     - Low Band (20Hz-1kHz): Base rotation patterns
     - Mid Band (1-3kHz): Early warning indicators
     - High Band (3-5kHz): Critical damage signatures
   - Interactive frequency spectrum analysis with zoom capabilities

3. **Degradation Analysis Layer**
   - Comprehensive tracking of bearing deterioration through:
     - Stability progression monitoring
     - Rate change analysis
     - Cross-channel correlation tracking
   - Custom visualization components for different failure modes:
     - Inner race failure patterns
     - Roller element degradation
     - Outer race wear characteristics

### Advanced Features

1. **Intelligent Alert System**
   - Real-time monitoring of critical thresholds
   - Multi-stage warning system based on:
     - Frequency band energy distributions
     - Kurtosis progression patterns
     - Channel stability metrics

2. **Predictive Analytics Integration**
   - Machine learning predictions visualization
   - Accuracy tracking across bearing lifetime
   - Interactive prediction vs. actual comparisons
   - Feature importance visualization
   - Error distribution analysis

3. **Cross-Channel Analysis**
   - Synchronized multi-channel visualization
   - Channel correlation tracking
   - Phase relationship analysis
   - Coupled degradation pattern recognition

### Technical Stack

1. **Frontend Implementation**
   - Django templating engine with dynamic content rendering
   - Interactive Plotly.js visualizations integrated into Django templates
   - Custom CSS implementation for specialized visualization components
   - Real-time data updates through JSON integration

2. **Backend Architecture**
   - Django-based data processing pipeline
   - Custom signal processing modules for real-time analysis
   - Optimized JSON data storage for rapid retrieval
   - Integrated testing framework with PyTest

3. **AWS Infrastructure**
   - Load-balanced deployment on ECS
   - ECR integration for container management
   - Automated scaling based on demand
   - High-availability configuration

4. **CI/CD Implementation**
   Two-stage pipeline:

   **Quality Assurance (CI)**
   - Automated code quality checks
   - PyTest integration for comprehensive testing
   - Custom test suite covering:
     - Data processing validation
     - Visualization integrity
     - Error handling scenarios

   **Deployment Pipeline (CD)**
   - Automated ECR builds
   - Blue-green deployment strategy
   - Health check integration
   - Automated rollback capabilities

### Visualization Components

1. **Time Domain Analysis**
   - Raw signal visualizations
   - Amplitude progression tracking
   - Multi-channel comparison capabilities

2. **Frequency Domain Analysis**
   - Interactive FFT visualizations
   - Band-specific energy tracking
   - Frequency correlation analysis

3. **Statistical Analysis**
   - Feature correlation matrix visualization
   - Degradation pattern recognition
   - Prediction accuracy tracking

4. **Health Monitoring**
   - Real-time status indicators
   - Predictive timeline visualization
   - Maintenance scheduling assistance

### Technologies
- Django
- Pytest
- Github Actions
- Docker 
- AWS Elastic Container Registry and Service (ECR & ECS)

This dashboard serves as the visual interface for our bearing analysis system, transforming complex vibration data into actionable maintenance insights through sophisticated visualization and monitoring capabilities. It represents a complete integration of advanced signal processing, machine learning predictions, and interactive data visualization techniques.