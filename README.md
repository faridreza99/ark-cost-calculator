# Seafood Cost Calculator

A streamlit application for Ark Sea Food Limited that calculates the cost of seafood products based on various parameters.

## Features

- **Products Management**: Add, edit, and delete products with their raw material size ranges
- **Rate Chart Management**: Set and modify rates for different sizes of raw materials
- **Variables Management**: Configure calculation variables like USD Rate, overhead costs, and freight rates
- **Cost Calculator**: Calculate costs for specific products or all products at once

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   or
   ```
   pip install streamlit pandas numpy
   ```

## Usage

Run the application with:
```
streamlit run app.py
```

## Calculation Formula

The cost is calculated using the following formula:

1. **Raw Material Cost** = Sum of raw material cost / Count of raw material cost
2. **FOB Cost in Tk.** = Raw Material Cost + Variable Overhead + Fixed Overhead
3. **FOB Cost in USD** = FOB Cost in Tk. / USD Rate
4. **Subsidy** = FOB Cost in USD * Subsidy Rate
5. **Net FOB Cost in USD** = FOB Cost in USD - Subsidy
6. **Final Cost** = Net FOB Cost in USD + Freight per Kg