import os
import sys

# Set Qt API to PyQt6 before importing webview
os.environ['QT_API'] = 'pyqt6'

import webview
import json
import math
from typing import List, Tuple, Dict, Any

# Import calculation functions from calc module
sys.path.insert(0, os.path.dirname(__file__))
from calc import (
    cross, rectiOpline, qline, striOpline, vlEqui,
    rectify, strip
)


def rectify_with_points(rl, vle, xD, ql, max_iter=1000) -> Tuple[float, int, List[Tuple[float, float]]]:
    """Rectifying section calculation with data points for McCabe-Thiele diagram."""
    xe, _ = cross(rl, ql)
    xj, i = vle(xD), 0
    points = [(xD, vle(xD))]  # Start at (xD, yD)
    
    while xj > xe and i < max_iter:
        i += 1
        _, yj = cross(rl, lambda x, y: x - xj)
        points.append((xj, yj))
        xj = vle(yj)
        points.append((xj, yj))
    
    return xj, i, points


def strip_with_points(sl, vle, xj_start, xW, max_iter=1000) -> Tuple[float, int, List[Tuple[float, float]]]:
    """Stripping section calculation with data points for McCabe-Thiele diagram."""
    i = 0
    xj = xj_start
    points = []
    
    while xj > xW and i < max_iter:
        i += 1
        _, yj = cross(sl, lambda x, y: x - xj)
        points.append((xj, yj))
        xj = vle(yj)
        points.append((xj, yj))
    
    return xj, i, points


def calculate_plate_numbers(params: Dict[str, float]) -> Dict[str, Any]:
    """Main calculation function that returns results and data for plotting."""
    import sys
    try:
        sys.stderr.write(f"calculate_plate_numbers: starting with params {params}\n")
        sys.stderr.flush()
        R = params['R']
        q = params['q']
        alpha = params['alpha']
        xD = params['xD']
        xF = params['xF']
        xW = params['xW']
        
        # Create lines
        rl = rectiOpline(R=R, xD=xD)
        ql = qline(q=q, xF=xF)
        sl = striOpline(rl=rl, ql=ql, xW=xW)
        vle = vlEqui(alpha=alpha)
        
        # Calculate with points
        xn, n, rect_points = rectify_with_points(rl, vle, xD, ql)
        xm, m, strip_points = strip_with_points(sl, vle, xn, xW)
        
        # Generate equilibrium line data
        y_eq = [i/100 for i in range(101)]
        x_eq = [vle(y) for y in y_eq]
        
        # Generate operating lines data
        x_range = [xW + (xD - xW) * i/100 for i in range(101)]
        y_rect = [(R*x + xD)/(R+1) for x in x_range]  # Rectifying line: y = (R*x + xD)/(R+1)
        
        # Stripping line: y = ((q/(q-1))*x - xF/(q-1)) but need intersection point
        # Actually we have sl line defined, but we can compute y for given x
        y_strip = []
        for x in x_range:
            # Find y from sl(x,y)=0
            # sl is defined as (yi-xW)*(x-xW) - (xi-xW)*(y-xW) = 0
            # where (xi, yi) is intersection of rl and ql
            xi, yi = cross(rl, ql)
            if abs(xi - xW) < 1e-12:
                y = yi  # vertical line case
            else:
                y = xW + (yi - xW) * (x - xW) / (xi - xW)
            y_strip.append(y)
        
        # Combine all points for staircase
        staircase_points = rect_points + strip_points
        
        return {
            'success': True,
            'results': {
                'Nt': n + m,
                'Nf': n + 1,
                'Nr': n,
                'Ns': m
            },
            'plot_data': {
                'equilibrium': {'x': x_eq, 'y': y_eq},
                'rectifying': {'x': x_range, 'y': y_rect},
                'stripping': {'x': x_range, 'y': y_strip},
                'staircase': [{'x': p[0], 'y': p[1]} for p in staircase_points],
                'intersection': {'x': xi, 'y': yi}  # intersection point
            }
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"ERROR in calculate_plate_numbers: {error_msg}", file=sys.stderr)
        print(f"Traceback: {traceback_msg}", file=sys.stderr)
        sys.stderr.flush()
        return {
            'success': False,
            'error': error_msg
        }


def save_results_to_file(results_text: str) -> str:
    """Save calculation results to a text file."""
    try:
        file_path = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            directory='/',
            save_filename='distillation_results.txt',
            file_types=('Text files (*.txt)', 'All files (*.*)')
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(results_text)
            return f"Results saved to {file_path}"
        else:
            return "Save cancelled"
    except Exception as e:
        return f"Error saving file: {str(e)}"


# HTML template with embedded JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Distillation Column Calculator</title>
    <script src="https://cdn.plot.ly/plotly-2.27.1.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .input-section {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .input-group {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input {
            padding: 8px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
        }
        .button-section {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        .calculate-btn {
            background-color: #2ecc71;
            color: white;
        }
        .calculate-btn:hover {
            background-color: #27ae60;
        }
        .save-btn {
            background-color: #3498db;
            color: white;
        }
        .save-btn:hover {
            background-color: #2980b9;
        }
        .export-btn {
            background-color: #9b59b6;
            color: white;
        }
        .export-btn:hover {
            background-color: #8e44ad;
        }
        .results-section {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }
        .result-item {
            text-align: center;
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .result-label {
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .result-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        #chart {
            width: 100%;
            height: 500px;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Distillation Column Calculator</h1>
        
        <div class="input-section">
            <div class="input-group">
                <label for="R">Reflux Ratio (R)</label>
                <input type="number" id="R" step="0.01" value="2.0">
            </div>
            <div class="input-group">
                <label for="q">Feed Thermal Condition (q)</label>
                <input type="number" id="q" step="0.01" value="0.5">
            </div>
            <div class="input-group">
                <label for="alpha">Relative Volatility (α)</label>
                <input type="number" id="alpha" step="0.01" value="2.5">
            </div>
            <div class="input-group">
                <label for="xD">Distillate Composition (xD)</label>
                <input type="number" id="xD" step="0.0001" value="0.95">
            </div>
            <div class="input-group">
                <label for="xF">Feed Composition (xF)</label>
                <input type="number" id="xF" step="0.0001" value="0.5">
            </div>
            <div class="input-group">
                <label for="xW">Bottoms Composition (xW)</label>
                <input type="number" id="xW" step="0.0001" value="0.05">
            </div>
        </div>
        
        <div class="button-section">
            <button class="calculate-btn" onclick="calculate()">Calculate Theoretical Plates</button>
            <button class="save-btn" onclick="saveResults()">Save Results as Text</button>
            <button class="export-btn" onclick="exportChart()">Export Chart as PNG</button>
        </div>
        
        <div id="status" class="status"></div>
        
        <div class="results-section">
            <div class="result-item">
                <div class="result-label">Total Plates (Nt)</div>
                <div class="result-value" id="Nt">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">Feed Plate (Nf)</div>
                <div class="result-value" id="Nf">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">Rectifying Plates (Nr)</div>
                <div class="result-value" id="Nr">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">Stripping Plates (Ns)</div>
                <div class="result-value" id="Ns">-</div>
            </div>
        </div>
        
        <div id="chart"></div>
    </div>
    
    <script>
        let plotData = null;
        
        function showStatus(message, isError = false) {
            const statusEl = document.getElementById('status');
            statusEl.textContent = message;
            statusEl.className = `status ${isError ? 'error' : 'success'}`;
            statusEl.style.display = 'block';
            setTimeout(() => {
                statusEl.style.display = 'none';
            }, 5000);
        }
        
        function getInputValues() {
            return {
                R: parseFloat(document.getElementById('R').value),
                q: parseFloat(document.getElementById('q').value),
                alpha: parseFloat(document.getElementById('alpha').value),
                xD: parseFloat(document.getElementById('xD').value),
                xF: parseFloat(document.getElementById('xF').value),
                xW: parseFloat(document.getElementById('xW').value)
            };
        }
        
        function validateInputs(params) {
            for (const [key, value] of Object.entries(params)) {
                if (isNaN(value)) {
                    return `${key} must be a valid number`;
                }
            }
            if (params.xD <= params.xW) {
                return 'xD must be greater than xW';
            }
            if (params.xF <= params.xW || params.xF >= params.xD) {
                return 'xF must be between xW and xD';
            }
            if (params.alpha <= 1) {
                return 'α (relative volatility) must be greater than 1';
            }
            if (params.R < 0) {
                return 'Reflux ratio R must be non-negative';
            }
            return null;
        }
        
        function updateResults(results) {
            document.getElementById('Nt').textContent = results.Nt;
            document.getElementById('Nf').textContent = results.Nf;
            document.getElementById('Nr').textContent = results.Nr;
            document.getElementById('Ns').textContent = results.Ns;
        }
        
        function plotChart(plotData) {
            const equilibriumTrace = {
                x: plotData.equilibrium.x,
                y: plotData.equilibrium.y,
                mode: 'lines',
                name: 'Equilibrium Line (y=x)',
                line: {color: '#e74c3c', width: 3}
            };
            
            const rectifyingTrace = {
                x: plotData.rectifying.x,
                y: plotData.rectifying.y,
                mode: 'lines',
                name: 'Rectifying Line',
                line: {color: '#3498db', width: 3, dash: 'dash'}
            };
            
            const strippingTrace = {
                x: plotData.stripping.x,
                y: plotData.stripping.y,
                mode: 'lines',
                name: 'Stripping Line',
                line: {color: '#2ecc71', width: 3, dash: 'dash'}
            };
            
            const staircaseTrace = {
                x: plotData.staircase.map(p => p.x),
                y: plotData.staircase.map(p => p.y),
                mode: 'lines+markers',
                name: 'McCabe-Thiele Steps',
                line: {color: '#f39c12', width: 2},
                marker: {size: 6, color: '#f39c12'}
            };
            
            const intersectionTrace = {
                x: [plotData.intersection.x],
                y: [plotData.intersection.y],
                mode: 'markers',
                name: 'Intersection',
                marker: {size: 10, color: '#9b59b6'}
            };
            
            const layout = {
                title: 'McCabe-Thiele Diagram',
                xaxis: {
                    title: 'Liquid Mole Fraction (x)',
                    range: [0, 1],
                    gridcolor: '#ecf0f1'
                },
                yaxis: {
                    title: 'Vapor Mole Fraction (y)',
                    range: [0, 1],
                    gridcolor: '#ecf0f1'
                },
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                showlegend: true,
                legend: {x: 0.02, y: 0.98}
            };
            
            Plotly.newPlot('chart', [
                equilibriumTrace,
                rectifyingTrace,
                strippingTrace,
                staircaseTrace,
                intersectionTrace
            ], layout);
        }
        
        function calculate() {
            const params = getInputValues();
            const error = validateInputs(params);
            if (error) {
                showStatus(error, true);
                return;
            }
            
            // Check if pywebview API is available
            if (!window.pywebview || !window.pywebview.api) {
                showStatus('Error: Python API not ready yet. Please wait a moment and try again.', true);
                return;
            }
            
            try {
                // Call Python function via pywebview API
                const resultOrPromise = window.pywebview.api.calculate_plate_numbers(params);
                
                // Handle both direct result and Promise
                const handleResult = (result) => {
                    // Check if result is valid
                    if (!result) {
                        showStatus('Error: No response from Python calculation', true);
                        return;
                    }
                    
                    if (result.success) {
                        updateResults(result.results);
                        plotData = result.plot_data;
                        plotChart(plotData);
                        showStatus('Calculation successful!');
                    } else {
                        // Check if error property exists
                        const errorMsg = result.error ? result.error : 'Unknown error';
                        // Debug: show result structure for troubleshooting
                        const debugInfo = `Error: ${errorMsg} (result keys: ${Object.keys(result).join(', ')}, success type: ${typeof result.success})`;
                        showStatus(debugInfo, true);
                    }
                };
                
                // Check if it's a Promise
                if (resultOrPromise && typeof resultOrPromise.then === 'function') {
                    // It's a Promise, wait for it
                    resultOrPromise
                        .then(handleResult)
                        .catch(e => {
                            showStatus('Error in Promise: ' + e.toString(), true);
                        });
                } else {
                    // It's a direct result
                    handleResult(resultOrPromise);
                }
            } catch (e) {
                showStatus('Error calling calculation: ' + e.toString(), true);
            }
        }
        
        function saveResults() {
            if (!plotData) {
                showStatus('Please calculate first before saving', true);
                return;
            }
            
            // Check if pywebview API is available
            if (!window.pywebview || !window.pywebview.api) {
                showStatus('Error: Python API not ready yet. Please wait a moment and try again.', true);
                return;
            }
            
            const resultsText = `Distillation Column Calculation Results
===========================================
Parameters:
Reflux Ratio (R): ${document.getElementById('R').value}
Feed Thermal Condition (q): ${document.getElementById('q').value}
Relative Volatility (α): ${document.getElementById('alpha').value}
Distillate Composition (xD): ${document.getElementById('xD').value}
Feed Composition (xF): ${document.getElementById('xF').value}
Bottoms Composition (xW): ${document.getElementById('xW').value}

Results:
Total Number of Theoretical Plates (Nt): ${document.getElementById('Nt').textContent}
Feed Plate Location (Nf): ${document.getElementById('Nf').textContent}
Number of Plates in Rectifying Section (Nr): ${document.getElementById('Nr').textContent}
Number of Plates in Stripping Section (including reboiler) (Ns): ${document.getElementById('Ns').textContent}
===========================================
Calculation performed using McCabe-Thiele method.`;
            
            try {
                const resultOrPromise = window.pywebview.api.save_results_to_file(resultsText);
                
                const handleResponse = (response) => {
                    showStatus(response);
                };
                
                // Check if it's a Promise
                if (resultOrPromise && typeof resultOrPromise.then === 'function') {
                    // It's a Promise, wait for it
                    resultOrPromise
                        .then(handleResponse)
                        .catch(e => {
                            showStatus('Error saving file: ' + e.toString(), true);
                        });
                } else {
                    // It's a direct result
                    handleResponse(resultOrPromise);
                }
            } catch (e) {
                showStatus('Error saving file: ' + e.toString(), true);
            }
        }
        
        function exportChart() {
            if (!plotData) {
                showStatus('Please calculate first before exporting chart', true);
                return;
            }
            
            try {
                Plotly.downloadImage('chart', {
                    format: 'png',
                    filename: 'mccabe_thiele_diagram',
                    height: 600,
                    width: 800
                });
                showStatus('Chart exported as PNG');
            } catch (e) {
                showStatus('Error exporting chart: ' + e.toString(), true);
            }
        }
        
        // Initialize with default values when pywebview API is ready
        function initializeApp() {
            if (window.pywebview && window.pywebview.api) {
                calculate();
            } else {
                showStatus('Python API not ready. Click "Calculate" to try again.', true);
            }
        }
        
        // Listen for pywebview ready event
        window.addEventListener('pywebviewready', initializeApp);
        
        // Also try to initialize immediately in case the event already fired
        if (window.pywebview && window.pywebview.api) {
            initializeApp();
        } else {
            // Set a timeout as fallback
            setTimeout(initializeApp, 1000);
        }
    </script>
</body>
</html>
"""


class Api:
    """API class to expose Python functions to JavaScript."""
    
    def calculate_plate_numbers(self, params):
        import sys
        sys.stderr.write(f"API.calculate_plate_numbers called with params: {params}\n")
        sys.stderr.flush()
        try:
            result = calculate_plate_numbers(params)
            sys.stderr.write(f"API.calculate_plate_numbers returning: {result}\n")
            sys.stderr.flush()
            return result
        except Exception as e:
            import traceback
            sys.stderr.write(f"API.calculate_plate_numbers exception: {e}\n")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()
            return {"success": False, "error": str(e)}
    
    def save_results_to_file(self, results_text):
        return save_results_to_file(results_text)


def main():
    """Main function to start the GUI application."""
    api = Api()
    
    # Create and start the webview window
    window = webview.create_window(
        'Distillation Column Calculator',
        html=HTML_TEMPLATE,
        js_api=api,
        width=1200,
        height=850,
        resizable=True,
        text_select=True
    )
    
    webview.start(debug=False, gui='qt')


if __name__ == '__main__':
    main()