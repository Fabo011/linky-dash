# Add new link to the CSV file
import pandas as pd

csv_file = 'data.csv'

def add_row_to_csv():
    # Collect user input
    linkname = input("Enter the link name: ")
    linkdescription = input("Enter the link tags: ")
    category = input("Enter the category: ")
    link = input("Enter the link: ")

    # Create a dictionary for the new row
    new_row = {
        'linkname': linkname,
        'linkdescription': linkdescription,
        'category': category,
        'link': link
    }

    # Convert the new row to a DataFrame
    new_row_df = pd.DataFrame([new_row])

    # Load the existing CSV file or create a new DataFrame if it doesn't exist
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['linkname', 'linkdescription', 'category', 'link'])

    # Concatenate the new row to the existing DataFrame
    df = pd.concat([df, new_row_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

    print(f"New row added to {csv_file}")

if __name__ == "__main__":
    add_row_to_csv()

