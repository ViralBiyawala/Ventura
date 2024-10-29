import os
from datetime import datetime
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Ensure the directory structure exists
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Save balance sheet to file
def save_balance_sheet(balance, shares_held, current_price, liabilities=0, initial_balance=0, report_type="daily"):
    """Saves the balance sheet at the end of each day or week into a text file."""
    
    # Define the folder and file name structure
    report_folder = os.path.join('reports', report_type)
    ensure_directory(report_folder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"balance_sheet_{timestamp}.txt"
    report_path = os.path.join(report_folder, report_filename)

    # Calculate values for the balance sheet
    assets = {
        "Cash": balance,
        "Investments (Stocks Held)": shares_held * current_price,
        "Total Assets": balance + (shares_held * current_price)
    }
    
    liabilities_dict = {
        "Short-term Debt": liabilities,
        "Total Liabilities": liabilities
    }
    
    shareholders_equity = {
        "Initial Investment": initial_balance,
        "Retained Earnings": assets["Total Assets"] - liabilities - initial_balance,
        "Total Shareholders' Equity": assets["Total Assets"] - liabilities
    }

    # Ensure the balance sheet equation holds: Assets = Liabilities + Shareholders' Equity
    assert assets["Total Assets"] == liabilities_dict["Total Liabilities"] + shareholders_equity["Total Shareholders' Equity"], \
        "Balance sheet does not balance!"

    # Save the balance sheet to a file
    with open(report_path, 'w') as report_file:
        report_file.write(f"---- {report_type.capitalize()} Balance Sheet ----\n\n")
        
        report_file.write("Assets:\n")
        for key, value in assets.items():
            report_file.write(f"{key}: ${value:.2f}\n")

        report_file.write("\nLiabilities:\n")
        for key, value in liabilities_dict.items():
            report_file.write(f"{key}: ${value:.2f}\n")

        report_file.write("\nShareholders' Equity:\n")
        for key, value in shareholders_equity.items():
            report_file.write(f"{key}: ${value:.2f}\n")

    # print(f"{report_type.capitalize()} balance sheet saved to {report_path}")

# Save the balance history plot
def save_balance_history_plot(balance_history, report_type="daily"):
    """Saves the plot of balance history as an image."""
    report_folder = os.path.join('reports', report_type)
    ensure_directory(report_folder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plot_filename = f"balance_history_{timestamp}.png"
    plot_path = os.path.join(report_folder, plot_filename)

    plt.figure(figsize=(10, 6))
    plt.plot(balance_history, label="Balance History")
    plt.xlabel('Time Step')
    plt.ylabel('Balance')
    plt.title('Balance Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(plot_path)
    plt.close()  # Close the figure after saving
    # print(f"Balance history plot saved to {plot_path}")

# Save balance sheet to CSV
def save_balance_sheet_csv(balance, shares_held, current_price, liabilities=0, initial_balance=0, report_type="daily"):
    """Saves the balance sheet at the end of each day or week into a CSV file."""
    
    # Define the folder and file name structure
    report_folder = os.path.join('reports', report_type)
    ensure_directory(report_folder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"balance_sheet_{timestamp}.csv"
    report_path = os.path.join(report_folder, report_filename)

    # Calculate values for the balance sheet
    assets = {
        "Cash": balance,
        "Investments (Stocks Held)": shares_held * current_price,
        "Total Assets": balance + (shares_held * current_price)
    }
    
    liabilities_dict = {
        "Short-term Debt": liabilities,
        "Total Liabilities": liabilities
    }
    
    shareholders_equity = {
        "Initial Investment": initial_balance,
        "Retained Earnings": assets["Total Assets"] - liabilities - initial_balance,
        "Total Shareholders' Equity": assets["Total Assets"] - liabilities
    }

    # Ensure the balance sheet equation holds: Assets = Liabilities + Shareholders' Equity
    assert assets["Total Assets"] == liabilities_dict["Total Liabilities"] + shareholders_equity["Total Shareholders' Equity"], \
        "Balance sheet does not balance!"

    # Save the balance sheet to a CSV file
    with open(report_path, 'w', newline='') as csvfile:
        fieldnames = ['Category', 'Description', 'Amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'Category': 'Assets', 'Description': '', 'Amount': ''})
        for key, value in assets.items():
            writer.writerow({'Category': '', 'Description': key, 'Amount': value})

        writer.writerow({'Category': 'Liabilities', 'Description': '', 'Amount': ''})
        for key, value in liabilities_dict.items():
            writer.writerow({'Category': '', 'Description': key, 'Amount': value})

        writer.writerow({'Category': "Shareholders' Equity", 'Description': '', 'Amount': ''})
        for key, value in shareholders_equity.items():
            writer.writerow({'Category': '', 'Description': key, 'Amount': value})

    # print(f"{report_type.capitalize()} balance sheet saved to {report_path}")

# Save balance sheet to Excel
def save_balance_sheet_excel(balance, shares_held, current_price, liabilities=0, initial_balance=0, report_type="daily"):
    """Saves the balance sheet at the end of each day or week into an Excel file."""
    
    # Define the folder and file name structure
    report_folder = os.path.join('reports', report_type)
    ensure_directory(report_folder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"balance_sheet_{timestamp}.xlsx"
    report_path = os.path.join(report_folder, report_filename)

    # Calculate values for the balance sheet
    assets = {
        "Cash": balance,
        "Investments (Stocks Held)": shares_held * current_price,
        "Total Assets": balance + (shares_held * current_price)
    }
    
    liabilities_dict = {
        "Short-term Debt": liabilities,
        "Total Liabilities": liabilities
    }
    
    shareholders_equity = {
        "Initial Investment": initial_balance,
        "Retained Earnings": assets["Total Assets"] - liabilities - initial_balance,
        "Total Shareholders' Equity": assets["Total Assets"] - liabilities
    }

    # Ensure the balance sheet equation holds: Assets = Liabilities + Shareholders' Equity
    assert assets["Total Assets"] == liabilities_dict["Total Liabilities"] + shareholders_equity["Total Shareholders' Equity"], \
        "Balance sheet does not balance!"

    # Create a DataFrame for the balance sheet
    data = {
        'Category': ['Assets'] * len(assets) + ['Liabilities'] * len(liabilities_dict) + ["Shareholders' Equity"] * len(shareholders_equity),
        'Description': list(assets.keys()) + list(liabilities_dict.keys()) + list(shareholders_equity.keys()),
        'Amount': list(assets.values()) + list(liabilities_dict.values()) + list(shareholders_equity.values())
    }
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    df.to_excel(report_path, index=False)
    # print(f"{report_type.capitalize()} balance sheet saved to {report_path}")