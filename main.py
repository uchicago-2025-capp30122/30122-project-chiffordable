import os

def run_visualizations():
    """
    Runs the dashboard script.
    """
    print("\n📊 Running dashboard...\n")
    os.system("python visualizations/dash_layout.py")  

def update_zillow_data():
    """
    Runs the Zillow scraper after showing a warning.
    """
    print("\n 🛑 WARNING: \n   Zillow headers might have changed.\n   If scraping fails, update headers in `zillow.py`.")
    print(" \n⏳ Scraping could take approximately 25 minutes to complete,\n   We wolud do all the scrapes for each listing in the City of Chicago \n   (12k listings)\n")
    
    # Ask for user confirmation
    choice = input("Do you want to update the Zillow data? (yes/no): ").strip().lower()
    
    if choice in ["yes", "y"]:
        print("\n🚀 Starting Zillow scraper...\n")
        os.system("PYTHONPATH=. python -m extracting.zillow")
        print("\n✅ Zillow data update complete!\n")
    else:
        print("\n⏩ Skipping Zillow scraper. Using existing data.\n")

def main():
    """
    Main function to run visualizations and optionally update Zillow data.
    """
    print("🔹 Welcome to the Chicago Rental Data Dashboard 🔹\n")

    # Ask the user if the want to update the Livability data

    # Ask the user if the want to update the CMAP data
    
    # Ask the user if they want to update the Zillow data
    update_zillow_data()
    
    # Run visualizations
    run_visualizations()

if __name__ == "__main__":
    main()