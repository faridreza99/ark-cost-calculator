import streamlit as st
import pandas as pd
import numpy as np

# Set page title and configuration
st.set_page_config(
    page_title="Seafood Cost Calculator",
    page_icon="🦐",
    layout="wide"
)

# Initialize session state for data persistence
if 'products' not in st.session_state:
    # Default product data as mentioned in the requirements
    st.session_state.products = pd.DataFrame({
        'Product': ['Product 1', 'Product 2', 'Product 3', 'Product 4', 'Product 5'],
        'Smallest Raw Material': [13, 20, 18, 5, 9],
        'Largest Raw Material': [17, 24, 23, 10, 16]
    })

if 'rates' not in st.session_state:
    # Default rate data as mentioned in the requirements
    sizes = list(range(5, 25))
    rates = [1700, 1700, 1700, 1500, 1500, 1500, 1500, 1200, 1200, 1200, 
             1200, 950, 950, 950, 950, 950, 850, 850, 850, 850]
    st.session_state.rates = pd.DataFrame({
        'Size': sizes,
        'Rate (Tk.)': rates
    })

if 'variables' not in st.session_state:
    # Default variables as mentioned in the requirements
    st.session_state.variables = pd.DataFrame({
        'Variable': ['USD Rate', 'Variable Overhead', 'Fixed Overhead', 'Subsidy Rate', 'Freight per Kg'],
        'Value': ['122 Tk.', '100 Tk.', '80 Tk.', '8%', '$0.20']
    })

# Function to get clean numeric values from variables
def get_variable_value(variable_name):
    value = st.session_state.variables.loc[st.session_state.variables['Variable'] == variable_name, 'Value'].values[0]
    
    # Remove currency symbols and convert to numeric
    value = value.replace('Tk.', '').replace('$', '').replace('%', '').strip()
    return float(value)

# Function to calculate cost for a product
def calculate_cost(product_name):
    # Find the product in the products dataframe
    product = st.session_state.products[st.session_state.products['Product'] == product_name].iloc[0]
    
    # Get the raw material size range
    smallest = int(product['Smallest Raw Material'])
    largest = int(product['Largest Raw Material'])
    
    # Get all the sizes within the range
    sizes_needed = list(range(smallest, largest + 1))
    
    # Get the rates for these sizes
    rates_df = st.session_state.rates[st.session_state.rates['Size'].isin(sizes_needed)]
    
    # Calculate raw material cost as the average of rates
    if len(rates_df) > 0:
        raw_material_cost = sum(rates_df['Rate (Tk.)']) / len(rates_df)
    else:
        raw_material_cost = 0
    
    # Get variables needed for calculation
    usd_rate = get_variable_value('USD Rate')
    variable_overhead = get_variable_value('Variable Overhead')
    fixed_overhead = get_variable_value('Fixed Overhead')
    subsidy_rate = get_variable_value('Subsidy Rate') / 100  # Convert percentage to decimal
    freight_per_kg = get_variable_value('Freight per Kg')
    
    # Calculate using the formulas from the requirements
    fob_cost_tk = raw_material_cost + variable_overhead + fixed_overhead
    fob_cost_usd = fob_cost_tk / usd_rate
    subsidy = fob_cost_usd * subsidy_rate
    net_fob_cost_usd = fob_cost_usd - subsidy
    final_cost = net_fob_cost_usd + freight_per_kg
    
    return final_cost, {
        'Raw Material Cost (Tk.)': raw_material_cost,
        'FOB Cost (Tk.)': fob_cost_tk,
        'FOB Cost (USD)': fob_cost_usd,
        'Subsidy (USD)': subsidy,
        'Net FOB Cost (USD)': net_fob_cost_usd,
        'Freight per Kg (USD)': freight_per_kg,
        'Final Cost (USD)': final_cost
    }

# Main application with tabs for each page
st.title("🦐 Ark Sea Food Limited - Cost Calculator")

tab1, tab2, tab3, tab4 = st.tabs(["Products", "Rate Chart", "Variables", "Cost Output"])

with tab1:
    st.header("Products Management")
    st.write("Add, delete, or modify products and their raw material size ranges.")
    
    # Edit existing products
    with st.expander("Edit Existing Products", expanded=True):
        for i, row in st.session_state.products.iterrows():
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                product_name = st.text_input(f"Product {i}", value=row['Product'], key=f"product_name_{i}")
            with cols[1]:
                smallest = st.number_input(f"Smallest Size {i}", min_value=1, value=int(row['Smallest Raw Material']), key=f"smallest_{i}")
            with cols[2]:
                largest = st.number_input(f"Largest Size {i}", min_value=smallest, value=int(row['Largest Raw Material']), key=f"largest_{i}")
            with cols[3]:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.products = st.session_state.products.drop(i).reset_index(drop=True)
                    st.rerun()
            
            # Update the product data
            st.session_state.products.at[i, 'Product'] = product_name
            st.session_state.products.at[i, 'Smallest Raw Material'] = smallest
            st.session_state.products.at[i, 'Largest Raw Material'] = largest
    
    # Add new product
    with st.expander("Add New Product"):
        with st.form("add_product_form"):
            new_product = st.text_input("Product Name")
            new_smallest = st.number_input("Smallest Raw Material Size", min_value=1, value=5)
            new_largest = st.number_input("Largest Raw Material Size", min_value=new_smallest, value=10)
            
            submitted = st.form_submit_button("Add Product")
            if submitted and new_product:
                # Add new product to dataframe
                new_row = pd.DataFrame({
                    'Product': [new_product],
                    'Smallest Raw Material': [new_smallest],
                    'Largest Raw Material': [new_largest]
                })
                st.session_state.products = pd.concat([st.session_state.products, new_row], ignore_index=True)
                st.success(f"Added {new_product} to products list!")
                st.rerun()
    
    # Display current products table
    st.subheader("Current Products")
    st.dataframe(st.session_state.products, use_container_width=True)

with tab2:
    st.header("Rate Chart Management")
    st.write("Add, delete, or modify rates for different sizes of raw material.")
    
    # Edit existing rates
    with st.expander("Edit Existing Rates", expanded=True):
        # Group rates by pairs to make the form more compact
        total_rows = len(st.session_state.rates)
        for i in range(0, total_rows, 2):
            cols = st.columns(4)
            
            # First rate in the row
            with cols[0]:
                if i < total_rows:
                    st.write(f"Size {st.session_state.rates.at[i, 'Size']}")
            with cols[1]:
                if i < total_rows:
                    rate_value = st.number_input(f"Rate {i}", min_value=0, value=int(st.session_state.rates.at[i, 'Rate (Tk.)']), key=f"rate_{i}")
                    st.session_state.rates.at[i, 'Rate (Tk.)'] = rate_value
            
            # Second rate in the row (if available)
            with cols[2]:
                if i+1 < total_rows:
                    st.write(f"Size {st.session_state.rates.at[i+1, 'Size']}")
            with cols[3]:
                if i+1 < total_rows:
                    rate_value = st.number_input(f"Rate {i+1}", min_value=0, value=int(st.session_state.rates.at[i+1, 'Rate (Tk.)']), key=f"rate_{i+1}")
                    st.session_state.rates.at[i+1, 'Rate (Tk.)'] = rate_value
    
    # Add new rate
    with st.expander("Add New Rate"):
        with st.form("add_rate_form"):
            new_size = st.number_input("Size", min_value=1, value=25)
            new_rate = st.number_input("Rate (Tk.)", min_value=0, value=850)
            
            submitted = st.form_submit_button("Add Rate")
            if submitted:
                # Check if size already exists
                if new_size in st.session_state.rates['Size'].values:
                    st.error(f"Size {new_size} already exists. Please edit the existing entry.")
                else:
                    # Add new rate to dataframe
                    new_row = pd.DataFrame({
                        'Size': [new_size],
                        'Rate (Tk.)': [new_rate]
                    })
                    st.session_state.rates = pd.concat([st.session_state.rates, new_row], ignore_index=True)
                    # Sort by size
                    st.session_state.rates = st.session_state.rates.sort_values('Size').reset_index(drop=True)
                    st.success(f"Added rate for size {new_size}!")
                    st.rerun()
    
    # Delete rate
    with st.expander("Delete Rate"):
        with st.form("delete_rate_form"):
            size_to_delete = st.selectbox("Select Size to Delete", st.session_state.rates['Size'].tolist())
            submitted = st.form_submit_button("Delete Rate")
            if submitted:
                st.session_state.rates = st.session_state.rates[st.session_state.rates['Size'] != size_to_delete].reset_index(drop=True)
                st.success(f"Deleted rate for size {size_to_delete}!")
                st.rerun()
    
    # Display current rates table
    st.subheader("Current Rate Chart")
    st.dataframe(st.session_state.rates, use_container_width=True)

with tab3:
    st.header("Variables Management")
    st.write("Edit variables required for cost calculation.")
    
    # Edit variables
    with st.expander("Edit Variables", expanded=True):
        for i, row in st.session_state.variables.iterrows():
            variable_name = row['Variable']
            current_value = row['Value']
            
            # Create appropriate input fields based on variable type
            if 'USD Rate' in variable_name:
                new_value = st.text_input(f"{variable_name}", value=current_value, key=f"var_{i}", 
                                         help="Enter value in Tk.")
            elif 'Overhead' in variable_name:
                new_value = st.text_input(f"{variable_name}", value=current_value, key=f"var_{i}",
                                         help="Enter value in Tk.")
            elif 'Subsidy Rate' in variable_name:
                new_value = st.text_input(f"{variable_name}", value=current_value, key=f"var_{i}",
                                         help="Enter value as percentage, e.g., 8%")
            elif 'Freight' in variable_name:
                new_value = st.text_input(f"{variable_name}", value=current_value, key=f"var_{i}",
                                         help="Enter value in USD, e.g., $0.20")
            else:
                new_value = st.text_input(f"{variable_name}", value=current_value, key=f"var_{i}")
            
            # Update the variable in the dataframe
            st.session_state.variables.at[i, 'Value'] = new_value
    
    # Display current variables
    st.subheader("Current Variables")
    st.dataframe(st.session_state.variables, use_container_width=True)

with tab4:
    st.header("Cost Calculator")
    st.write("Select a product to calculate its cost based on the configured variables.")
    
    # Product selection and cost calculation
    product_options = st.session_state.products['Product'].tolist()
    selected_product = st.selectbox("Select Product", product_options)
    
    if st.button("Calculate Cost"):
        if selected_product:
            final_cost, cost_breakdown = calculate_cost(selected_product)
            
            # Display the result
            st.success(f"The final cost for {selected_product} is: ${final_cost:.2f} USD")
            
            # Display cost breakdown
            st.subheader("Cost Breakdown")
            breakdown_df = pd.DataFrame({
                'Component': list(cost_breakdown.keys()),
                'Value': [f"{value:.2f}" for value in cost_breakdown.values()]
            })
            st.dataframe(breakdown_df, use_container_width=True)
            
            # Visualization of cost components
            st.subheader("Cost Components")
            component_names = ['Raw Material', 'Variable Overhead', 'Fixed Overhead', 'Freight per Kg']
            component_values = [
                cost_breakdown['Raw Material Cost (Tk.)'] / get_variable_value('USD Rate'),
                get_variable_value('Variable Overhead') / get_variable_value('USD Rate'),
                get_variable_value('Fixed Overhead') / get_variable_value('USD Rate'),
                get_variable_value('Freight per Kg')
            ]
            
            # Create bar chart
            chart_data = pd.DataFrame({
                'Component': component_names,
                'USD Value': component_values
            })
            st.bar_chart(chart_data.set_index('Component'), use_container_width=True)
            
            # Display the formula explanation
            with st.expander("Formula Explanation"):
                st.markdown("""
                **Cost Calculation Formula:**
                
                1. **Raw Material Cost** = Sum of raw material cost / Count of raw material cost
                2. **FOB Cost in Tk.** = Raw Material Cost + Variable Overhead + Fixed Overhead
                3. **FOB Cost in USD** = FOB Cost in Tk. / USD Rate
                4. **Subsidy** = FOB Cost in USD * Subsidy Rate
                5. **Net FOB Cost in USD** = FOB Cost in USD - Subsidy
                6. **Final Cost** = Net FOB Cost in USD + Freight per Kg
                """)
        else:
            st.error("Please select a product first.")
    
    # Display the cost table for all products
    if st.button("Calculate All Products"):
        st.subheader("Cost Table for All Products")
        
        results = []
        for product in product_options:
            final_cost, _ = calculate_cost(product)
            results.append({"Product": product, "Cost (USD)": f"${final_cost:.2f}"})
        
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("© 2023 Ark Sea Food Limited | IT Executive Assignment")
