package com.example.calculator;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    private TextView display;
    private String currentNumber = "";
    private String operator = "";
    private String firstNumber = "";
    private boolean isNewOperation = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 初始化显示屏
        display = findViewById(R.id.display);

        // 初始化数字按钮
        int[] numberButtonIds = {
            R.id.btn0, R.id.btn1, R.id.btn2, R.id.btn3, R.id.btn4,
            R.id.btn5, R.id.btn6, R.id.btn7, R.id.btn8, R.id.btn9
        };

        for (int id : numberButtonIds) {
            findViewById(id).setOnClickListener(this);
        }

        // 初始化运算符按钮
        findViewById(R.id.btnAdd).setOnClickListener(this);
        findViewById(R.id.btnSubtract).setOnClickListener(this);
        findViewById(R.id.btnMultiply).setOnClickListener(this);
        findViewById(R.id.btnDivide).setOnClickListener(this);
        findViewById(R.id.btnEquals).setOnClickListener(this);
        findViewById(R.id.btnClear).setOnClickListener(this);
        findViewById(R.id.btnDelete).setOnClickListener(this);
        findViewById(R.id.btnDot).setOnClickListener(this);

        // 初始化显示
        display.setText("0");
    }

    @Override
    public void onClick(View v) {
        Button button = (Button) v;
        String buttonText = button.getText().toString();

        switch (v.getId()) {
            case R.id.btn0:
            case R.id.btn1:
            case R.id.btn2:
            case R.id.btn3:
            case R.id.btn4:
            case R.id.btn5:
            case R.id.btn6:
            case R.id.btn7:
            case R.id.btn8:
            case R.id.btn9:
                handleNumberInput(buttonText);
                break;

            case R.id.btnDot:
                handleDotInput();
                break;

            case R.id.btnAdd:
            case R.id.btnSubtract:
            case R.id.btnMultiply:
            case R.id.btnDivide:
                handleOperatorInput(buttonText);
                break;

            case R.id.btnEquals:
                handleEqualsInput();
                break;

            case R.id.btnClear:
                handleClearInput();
                break;

            case R.id.btnDelete:
                handleDeleteInput();
                break;
        }
    }

    private void handleNumberInput(String number) {
        if (isNewOperation) {
            currentNumber = number;
            isNewOperation = false;
        } else {
            if (currentNumber.equals("0")) {
                currentNumber = number;
            } else {
                currentNumber += number;
            }
        }
        display.setText(currentNumber);
    }

    private void handleDotInput() {
        if (isNewOperation) {
            currentNumber = "0.";
            isNewOperation = false;
        } else if (!currentNumber.contains(".")) {
            if (currentNumber.isEmpty()) {
                currentNumber = "0.";
            } else {
                currentNumber += ".";
            }
        }
        display.setText(currentNumber);
    }

    private void handleOperatorInput(String op) {
        if (!firstNumber.isEmpty() && !operator.isEmpty() && !isNewOperation) {
            // 如果有待处理的运算，先计算
            handleEqualsInput();
        }

        firstNumber = currentNumber.isEmpty() ? "0" : currentNumber;
        operator = op;
        isNewOperation = true;
    }

    private void handleEqualsInput() {
        if (firstNumber.isEmpty() || operator.isEmpty() || currentNumber.isEmpty()) {
            return;
        }

        try {
            double num1 = Double.parseDouble(firstNumber);
            double num2 = Double.parseDouble(currentNumber);
            double result = 0;

            switch (operator) {
                case "+":
                    result = num1 + num2;
                    break;
                case "-":
                    result = num1 - num2;
                    break;
                case "×":
                    result = num1 * num2;
                    break;
                case "÷":
                    if (num2 == 0) {
                        display.setText("错误：除零");
                        handleClearInput();
                        return;
                    }
                    result = num1 / num2;
                    break;
            }

            // 格式化结果显示
            String resultString;
            if (result == (long) result) {
                resultString = String.valueOf((long) result);
            } else {
                resultString = String.valueOf(result);
            }

            display.setText(resultString);
            currentNumber = resultString;
            firstNumber = "";
            operator = "";
            isNewOperation = true;

        } catch (NumberFormatException e) {
            display.setText("错误");
            handleClearInput();
        }
    }

    private void handleClearInput() {
        currentNumber = "";
        firstNumber = "";
        operator = "";
        isNewOperation = true;
        display.setText("0");
    }

    private void handleDeleteInput() {
        if (!currentNumber.isEmpty() && !isNewOperation) {
            currentNumber = currentNumber.substring(0, currentNumber.length() - 1);
            if (currentNumber.isEmpty()) {
                currentNumber = "";
                display.setText("0");
            } else {
                display.setText(currentNumber);
            }
        }
    }
}