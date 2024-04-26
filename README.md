# swe_summative: DeepFoot

DeepFoot is an educational tool that showcases the potential of machine learning and web development technologies in creating interactive and predictive applications. Ot uses a machine learning model trained on historical Premier League match data to predict the outcomes of upcoming matches on a week-by-week basis.

The frontend of the application provides a user-friendly interface where users can select a specific matchweek and view the predicted results for each match. The predictions include the likelihood of a home win/draw or an away win/draw, expressed as percentages.

The backend invloves a logistic regression model trained on various features such as team performance, goals scored, and previous season points. The model is continuously updated with the latest match data (obtained via API calls to football-data.org) to provide accurate predictions.

DeepFoot is designed to be used as an educational resource, demonstrating how machine learning algorithms can be integrated with web technologies to create practical and interactive applications. It aims to inspire and educate individuals about the possibilities and potential of combining these technologies in solving real-world problems.

## Features

- Predicts the likelihood of a home win/draw or an away win/draw for each match in a selected matchweek
- Utilizes a logistic regression model trained on historical Premier League match data
- Provides a user-friendly web interface for selecting matchweeks and viewing predictions
- Displays team names, and prediction percentages for each match

## Installation

1. Clone the repository:
  ```git clone https://github.com/DeliciousEarlGrey/swe_summative.git```

2. Navigate to the project directory:
   ```cd swe_summative```

3. Install the required dependencies:
   ```pip install -r requirements.txt```

4. Run the application:
   ```python prediction_algorithm.py```

5. Open your web browser and visit `http://localhost:5000` to access the DeepFoot application.

## Usage

1. Select a matchweek from the dropdown menu on the homepage.
2. View the predicted results for each match, including team names and confidence percentages.


## Configuration

The following configuration options are available:

- `API_ENDPOINT`: The URL endpoint for retrieving football data (default: "https://api.football-data.org/v2/")
- `TRAINING_SEASONS`: The range of seasons to use for training the machine learning model (default: ["2019-20", "2020-21"])
- `PREDICTION_SEASON`: The season for which predictions are generated (default: "2021-22")


## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions, suggestions, or feedback, please feel free to get in touch.
