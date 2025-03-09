import os


def run_visualizations():
    """
    Runs the dashboard script.
    """
    print("\n📊 Running dashboard...\n")
    os.system("python app/dash_app.py")


def main():
    """
    Main function to run visualizations and optionally update Zillow data.
    """
    print("\n\n🔹 Welcome to the Chicago Rental Data Dashboard 🔹\n")

    # Run visualizations
    run_visualizations()


if __name__ == "__main__":
    main()
