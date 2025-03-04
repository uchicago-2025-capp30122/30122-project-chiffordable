from pathlib import Path
import csv
import pytest

communities_data = Path(__file__).parent.parent / "extracted_data" / "cmap.csv"
age_headers = ["UND5","A5_19","A20_34", "A35_49","A50_64","A65_74","A75_84", "OV85"]
racial_headers = ["WHITE","HISP","BLACK", "ASIAN","OTHER"]

# testing sum of proportion of ages is 100%
def test_age_sums_100():
    with open(communities_data, "r") as cmap_data:
        reader = csv.DictReader(cmap_data)
        for row in reader:
            total_age = 0
            for age in age_headers:
                total_age += float(row[age])
            assert total_age == pytest.approx(100, abs=0.25)

# testing sum of proportion of races is 100%
def test_race_sums_100():
    with open(communities_data, "r") as cmap_data:
        reader = csv.DictReader(cmap_data)
        for row in reader:
            total_race = 0
            for race in racial_headers:
                total_race += float(row[race])
            assert total_race == pytest.approx(100, abs=0.25)