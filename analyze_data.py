import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Set pandas options to display the full content of long strings
pd.set_option('display.max_colwidth', None)  # Display full column width for long strings
pd.set_option('display.max_rows', None)      # Display all rows (if needed)
pd.set_option('display.max_columns', None)   # Display all columns

# Load the CSV
csv_filename = "Pokemon-Fusion-Strike.csv"
csv_filename = "Pokemon-Temporal-Forces.csv"
df = pd.read_csv(csv_filename)

# Display basic info
print(df.info())
print(df.describe())
print(df.isnull().sum())

# Sort by Expected Profit descending
df_sorted = df.sort_values(by='Expected Profit', ascending=False)
print(df_sorted.head())

# Filter cards with Expected Profit > $100
df_filtered = df[df['Expected Profit'] > 100]
print(df_filtered)

# Calculate Total Revenue and Profit Margin
df['Total Revenue'] = (3 * df['PSA 10 Price'] +
                       3 * df['PSA 9 Price'] +
                       4 * df['PSA 8 Price'])

df['Profit Margin (%)'] = (df['Expected Profit'] / df['Total Revenue']) * 100
print(df[['Card URL', 'Expected Profit', 'Total Revenue', 'Profit Margin (%)']].head())

# Handle missing data (example: drop rows with missing values)
df_cleaned = df.dropna()
print(df_cleaned.info())

# Summary statistics
average_profit = df['Expected Profit'].mean()
median_profit = df['Expected Profit'].median()
max_profit = df['Expected Profit'].max()
min_profit = df['Expected Profit'].min()

print(f"Average Expected Profit: ${average_profit:.2f}")
print(f"Median Expected Profit: ${median_profit:.2f}")
print(f"Maximum Expected Profit: ${max_profit:.2f}")
print(f"Minimum Expected Profit: ${min_profit:.2f}")

# Visualizations

# Histogram of Expected Profit
plt.figure(figsize=(10,6))
sns.histplot(df['Expected Profit'], bins=30, kde=True)
plt.title('Distribution of Expected Profit')
plt.xlabel('Expected Profit ($)')
plt.ylabel('Frequency')
plt.show()

# Scatter plot of Raw Price vs Expected Profit
plt.figure(figsize=(10,6))
sns.scatterplot(data=df, x='Raw Price', y='Expected Profit')
plt.title('Raw Price vs Expected Profit')
plt.xlabel('Raw Price ($)')
plt.ylabel('Expected Profit ($)')
plt.show()

# Bar plot of top 10 cards by Expected Profit
top10 = df_sorted.head(10)
plt.figure(figsize=(12,8))
sns.barplot(data=top10, x='Card URL', y='Expected Profit')
plt.xticks(rotation=90)
plt.title('Top 10 Cards by Expected Profit')
plt.xlabel('Card URL')
plt.ylabel('Expected Profit ($)')
plt.show()

# Save modified DataFrames
df_sorted.to_csv("Pokemon-Fusion-Strike_Sorted.csv", index=False)
df_filtered.to_csv("Pokemon-Fusion-Strike_Filtered.csv", index=False)
df.to_csv("Pokemon-Fusion-Strike_With_Metrics.csv", index=False)

