from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QTextEdit, QTabWidget)
from PyQt6.QtCore import Qt
import sys
from company_analyzer import CompanyMetrics, HistoricalData, CompanyAnalyzer

class CompanyAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Company Analyzer")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create tabs for input and results
        input_tab = QWidget()
        results_tab = QWidget()
        tabs.addTab(input_tab, "Input Data")
        tabs.addTab(results_tab, "Analysis Results")
        
        # Setup input form
        input_layout = QVBoxLayout(input_tab)
        self.setup_input_form(input_layout)
        
        # Setup results view
        results_layout = QVBoxLayout(results_tab)
        self.setup_results_view(results_layout)
        
        # Add analyze and export buttons
        button_layout = QHBoxLayout()
        analyze_btn = QPushButton("Analyze")
        export_btn = QPushButton("Export to Excel")
        analyze_btn.clicked.connect(self.perform_analysis)
        export_btn.clicked.connect(self.export_results)
        button_layout.addWidget(analyze_btn)
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)

    def setup_input_form(self, layout):
        metrics_group = QWidget()
        metrics_layout = QFormLayout(metrics_group)
        
        # Default values from MARI example
        default_values = {
            'current_price': 694.29,
            'market_cap': 833.58e9,
            'shares_outstanding': 1.2e9,
            'eps': 579.41,
            'book_value': 1694.74,
            'dividend_per_share': 232.00,
            'pe_ratio': 1.20,
            'pb_ratio': 0.25,
            'dividend_yield': 54.52,
            'debt_to_equity': 0.25,
            'current_ratio': 2.77,
            'interest_coverage': 33.83,
            'net_profit_margin': 43.23,
            'gross_profit_margin': 87.91,
            'total_assets': 254.6e9,
            'total_liabilities': 86.17e9,
            'equity': 168.43e9,
            'cash': 31.7e9,
            'debt': 672.38e6
        }
        
        # Create input fields for CompanyMetrics
        self.metric_inputs = {}
        for field, default_value in default_values.items():
            self.metric_inputs[field] = QLineEdit()
            self.metric_inputs[field].setText(str(default_value))
            metrics_layout.addRow(field.replace('_', ' ').title() + ':', 
                                self.metric_inputs[field])
        
        layout.addWidget(metrics_group)

    def setup_results_view(self, layout):
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def get_metrics_from_input(self):
        try:
            return CompanyMetrics(
                **{field: float(input.text()) 
                   for field, input in self.metric_inputs.items()}
            )
        except ValueError as e:
            self.results_text.setText(f"Error in input values: {str(e)}")
            return None

    def get_sample_historical_data(self):
        # Using sample historical data for demonstration
        return HistoricalData(
            years=[2019, 2020, 2021, 2022, 2023],
            revenue=[59.45e9, 72.03e9, 73.02e9, 95.13e9, 145.77e9],
            net_profit=[24.33e9, 30.31e9, 31.44e9, 33.06e9, 56.13e9],
            eps=[200.59, 227.23, 235.71, 247.84, 420.75],
            dividends=[6.00, 6.10, 141.00, 124.00, 147.00],
            book_value=[476.81, 698.26, 866.04, 980.92, 1262.55]
        )

    def perform_analysis(self):
        metrics = self.get_metrics_from_input()
        if metrics:
            historical = self.get_sample_historical_data()
            analyzer = CompanyAnalyzer(metrics, historical)
            report = analyzer.generate_report()
            
            # Display results
            result_text = "Analysis Results:\n\n"
            result_text += f"Investment Rating: {report['investment_rating']}\n"
            result_text += f"Total Score: {report['total_score']}\n\n"
            result_text += "Recommendations:\n"
            for rec in report['recommendations']:
                result_text += f"- {rec}\n"
            
            self.results_text.setText(result_text)
            self.report = report  # Store for export

    def export_results(self):
        if hasattr(self, 'report'):
            from company_analyzer import export_to_excel
            export_to_excel(self.report, 'company_analysis.xlsx')
            self.results_text.append("\nReport exported to company_analysis.xlsx")

def main():
    app = QApplication(sys.argv)
    window = CompanyAnalyzerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()