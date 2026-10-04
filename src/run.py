import config
from src.load import load_race
from src.clean import clean_laps, write_data_quality


def main():
    session, laps = load_race()
    total_laps = int(laps["LapNumber"].max())
    green_laps, dropped, log = clean_laps(laps, total_laps)
    write_data_quality("data_quality.md", log, dropped)
    for step, gone, left in log:
        print(f"{step:45s} dropped {gone:4d} remaining {left:4d}")
    return session, green_laps


if __name__ == "__main__":
    main()
