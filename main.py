import sys
import os
import joblib
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                             QFrame, QScrollArea, QMessageBox, QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon


class ModernChurnPredictorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Churn Predictor")
        self.setMinimumSize(1000, 800)
        self.model = None

        # Modern flat design style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2d3436;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #2d3436;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #00b894;
                background-color: #f8f9fa;
            }
            QLineEdit:hover {
                border: 2px solid #74b9ff;
            }
            QComboBox {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                padding: 10px;
                min-width: 150px;
                min-height: 24px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #00b894;
            }
            QComboBox:hover {
                border: 2px solid #74b9ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url('down_arrow.png');
                width: 12px;
                height: 12px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QFrame#mainFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dfe6e9;
            }
            QFrame#sectionFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                margin: 10px;
                padding: 15px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#predictButton {
                background-color: #00b894;
                color: white;
                border: none;
            }
            QPushButton#predictButton:hover {
                background-color: #00a885;
            }
            QPushButton#predictButton:disabled {
                background-color: #b2bec3;
            }
            QPushButton#clearButton {
                background-color: #ff7675;
                color: white;
                border: none;
            }
            QPushButton#clearButton:hover {
                background-color: #e66767;
            }
            QPushButton#modelButton {
                background-color: #6c5ce7;
                color: white;
                border: none;
            }
            QPushButton#modelButton:hover {
                background-color: #5f50d9;
            }
            QLabel#titleLabel {
                color: #2d3436;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
            QLabel#sectionLabel {
                color: #00b894;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 0;
            }
            QLabel#resultLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
            }
        """)

        # Main layout setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("sectionFrame")
        header_layout = QHBoxLayout(header_frame)

        # Title and model selection
        title_label = QLabel("Customer Churn Predictor")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)

        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        self.model_label = QLabel("No model selected")
        self.model_label.setStyleSheet("color: #636e72; font-style: italic;")
        model_layout.addWidget(self.model_label)

        select_model_btn = QPushButton("Select Model")
        select_model_btn.setObjectName("modelButton")
        select_model_btn.clicked.connect(self.load_model)
        model_layout.addWidget(select_model_btn)

        header_layout.addWidget(model_widget)
        main_layout.addWidget(header_frame)

        # Create main content area
        content_frame = QFrame()
        content_frame.setObjectName("mainFrame")
        content_layout = QVBoxLayout(content_frame)

        # Scroll area for input fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Input sections
        self.inputs = {}

        # Account Section
        account_frame = self.create_section_frame("Account Information")
        self.inputs['Account length'] = self.add_input_field("Account Length", account_frame.layout())
        scroll_layout.addWidget(account_frame)

        # Service Plans Section
        plans_frame = self.create_section_frame("Service Plans")
        plans_layout = plans_frame.layout()
        self.inputs['International plan'] = self.add_combo_field("International Plan", ['No', 'Yes'], plans_layout)
        self.inputs['Voice mail plan'] = self.add_combo_field("Voice Mail Plan", ['No', 'Yes'], plans_layout)
        self.inputs['Number vmail messages'] = self.add_input_field("Voice Mail Messages", plans_layout)
        scroll_layout.addWidget(plans_frame)

        # Usage Metrics Section
        usage_frame = self.create_section_frame("Usage Metrics")
        usage_layout = usage_frame.layout()

        # Day Usage
        self.add_subsection_label("Day Usage", usage_layout)
        self.inputs['Total day minutes'] = self.add_input_field("Total Minutes", usage_layout)
        self.inputs['Total day calls'] = self.add_input_field("Total Calls", usage_layout)

        # Evening Usage
        self.add_subsection_label("Evening Usage", usage_layout)
        self.inputs['Total eve minutes'] = self.add_input_field("Total Minutes", usage_layout)
        self.inputs['Total eve calls'] = self.add_input_field("Total Calls", usage_layout)

        # Night Usage
        self.add_subsection_label("Night Usage", usage_layout)
        self.inputs['Total night minutes'] = self.add_input_field("Total Minutes", usage_layout)
        self.inputs['Total night calls'] = self.add_input_field("Total Calls", usage_layout)

        scroll_layout.addWidget(usage_frame)

        # International Usage Section
        intl_frame = self.create_section_frame("International Usage")
        intl_layout = intl_frame.layout()
        self.inputs['Total intl minutes'] = self.add_input_field("Total Minutes", intl_layout)
        self.inputs['Total intl calls'] = self.add_input_field("Total Calls", intl_layout)
        scroll_layout.addWidget(intl_frame)

        # Customer Service Section
        service_frame = self.create_section_frame("Customer Service")
        self.inputs['Customer_service_calls'] = self.add_input_field("Service Calls", service_frame.layout())
        scroll_layout.addWidget(service_frame)

        scroll.setWidget(scroll_widget)
        content_layout.addWidget(scroll)

        # Button section
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(15)

        clear_btn = QPushButton("Clear Form")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self.clear_form)

        self.predict_btn = QPushButton("Predict Churn")
        self.predict_btn.setObjectName("predictButton")
        self.predict_btn.clicked.connect(self.predict_churn)
        self.predict_btn.setEnabled(False)

        button_layout.addWidget(clear_btn)
        button_layout.addWidget(self.predict_btn)
        content_layout.addWidget(button_container)

        # Result section
        self.result_label = QLabel()
        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.result_label)

        main_layout.addWidget(content_frame)

    def create_section_frame(self, title):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)

        label = QLabel(title)
        label.setObjectName("sectionLabel")
        layout.addWidget(label)

        return frame

    def add_subsection_label(self, text, layout):
        label = QLabel(text)
        label.setStyleSheet("""
            color: #636e72;
            font-size: 14px;
            font-weight: bold;
            padding-top: 10px;
        """)
        layout.addWidget(label)

    def add_input_field(self, label_text, layout):
        container = QWidget()
        field_layout = QHBoxLayout(container)
        field_layout.setSpacing(15)

        label = QLabel(label_text)
        label.setMinimumWidth(150)
        input_field = QLineEdit()

        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        layout.addWidget(container)

        return input_field

    def add_combo_field(self, label_text, items, layout):
        container = QWidget()
        field_layout = QHBoxLayout(container)
        field_layout.setSpacing(15)

        label = QLabel(label_text)
        label.setMinimumWidth(150)
        combo = QComboBox()
        combo.addItems(items)

        field_layout.addWidget(label)
        field_layout.addWidget(combo)
        layout.addWidget(container)

        return combo

    def clear_form(self):
        for input_field in self.inputs.values():
            if isinstance(input_field, QLineEdit):
                input_field.clear()
            elif isinstance(input_field, QComboBox):
                input_field.setCurrentIndex(0)
        self.result_label.clear()
        self.result_label.setStyleSheet("")

    def load_model(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select Model File",
                "",
                "Model Files (*.pkl *.joblib);;All Files (*)"
            )

            if file_name:
                self.model = joblib.load(file_name)
                model_name = os.path.basename(file_name)
                self.model_label.setText(f"Model: {model_name}")
                self.model_label.setStyleSheet("color: #00b894; font-weight: bold;")
                self.predict_btn.setEnabled(True)
                QMessageBox.information(self, "Success", f"Model '{model_name}' loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading model: {str(e)}")
            self.model = None
            self.model_label.setText("No model selected")
            self.model_label.setStyleSheet("color: #636e72; font-style: italic;")
            self.predict_btn.setEnabled(False)

    def process_customer_service_calls(self, calls):
        if calls <= 0:
            return 0
        elif calls <= 2:
            return 1
        elif calls <= 4:
            return 2
        elif calls <= 6:
            return 3
        else:
            return 4

    def predict_churn(self):
        if self.model is None:
            QMessageBox.warning(self, "No Model", "Please select a model first!")
            return

        try:
            calls = int(self.inputs['Customer_service_calls'].text())

            input_data = {
                'Account length': int(self.inputs['Account length'].text()),
                'International plan': 1 if self.inputs['International plan'].currentText() == 'Yes' else 0,
                'Voice mail plan': 1 if self.inputs['Voice mail plan'].currentText() == 'Yes' else 0,
                'Number vmail messages': int(self.inputs['Number vmail messages'].text()),
                'Total day minutes': float(self.inputs['Total day minutes'].text()),
                'Total day calls': int(self.inputs['Total day calls'].text()),
                'Total eve minutes': float(self.inputs['Total eve minutes'].text()),
                'Total eve calls': int(self.inputs['Total eve calls'].text()),
                'Total night minutes': float(self.inputs['Total night minutes'].text()),
                'Total night calls': int(self.inputs['Total night calls'].text()),
                'Total intl minutes': float(self.inputs['Total intl minutes'].text()),
                'Total intl calls': int(self.inputs['Total intl calls'].text()),
                'Customer_service_calls_binned_encoded': self.process_customer_service_calls(calls)
            }

            df = pd.DataFrame([input_data])
            prediction = self.model.predict(df)[0]
            probability = self.model.predict_proba(df)[0]

            if prediction == 1:
                self.result_label.setStyleSheet("""
                    QLabel#resultLabel {
                        background-color: #fff3f3;
                        color: #ff4757;
                        border: 2px solid #ff4757;
                    }
                """)
                result_text = f"High Risk of Churn (Probability: {probability[1]:.1%})"
            else:
                self.result_label.setStyleSheet("""
                    QLabel#resultLabel {
                        background-color: #f0fff0;
                        color: #2ed573;
                        border: 2px solid #2ed573;
                    }
                """)
                result_text = f"Low Risk of Churn (Probability: {probability[0]:.1%})"

            self.result_label.setText(result_text)

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please ensure all fields contain valid numeric values."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during prediction: {str(e)}"
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))

    # Create and show the main window
    window = ModernChurnPredictorApp()
    window.show()

    sys.exit(app.exec())