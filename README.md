# Project_Quant-model_1
This is my first day traiding model that predicts the out come of the next day using OHLCV stock data mertrics.
This is a tutorial of how to setup the model so that it could trade stocks:
1) Model setup
   
  a) Model1_NAS100_BUY.py
  
    1) Enter your Alpaca API key and secret key on lines 19 and 73
    2) On line 14, enter the path to the "Nasdaq 100 (NDX).csv" file (included in the repository)
    3) On line 24, enter the path to the trained model file:
      xgboost_model1.json
    NOTE: This script is responsible for selecting and buying stocks based on the model’s predictions.

  b) Model1_SELL.py
  
    Enter your Alpaca API key and secret key on lines 4 and 5.
    NOTE: This script handles selling positions before market close.
    
2) Automated execution (optional)
  To automate the buying and selling process, you can use Windows Task Scheduler.
  This is the setup I used:
    Open Task Scheduler (Press Windows + R, then enter taskschd.msc), then create two separate tasks:
      1)One for buying stocks before market open
      2)One for selling stocks before market close
      ⚠️ Important: Select “Create Task”, not “Create Basic Task”
    a) General tab
      Give the task a name (e.g. Model1_Buy / Model1_Sell)
      Check:
        Run whether user is logged on or not
        Run with highest privileges
        (This allows the script to run even if you are not logged in.)
    b) Triggers tab
      Create a new trigger
      Set:
        Begin the task: On a schedule
        Weekly
        Select Monday–Friday
        Set the time:
        Buy task → shortly before market open
        Sell task → shortly before market close
    c) Actions tab
      Create a new action:
      Action: Start a program
      Program/script: Path to your Python executable (put all of the files in a virtual environment)
      Add arguments: Path to the script (Model1_NAS100_BUY.py or Model1_SELL.py)
      Start in: Directory containing the script
    d) Conditions / Settings tabs
      Disable any options that could prevent the task from running (e.g. “Start the task only if the computer is on AC power”)
      Allow the task to be run on demand

Notes:
This project is for educational purposes only. Ensure you only use alpacas paper trading account.
The model uses historical price and volume data and does not guarantee profitability.
Make sure your Python environment includes all required dependencies before running the scripts.
