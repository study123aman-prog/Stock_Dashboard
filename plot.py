import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/TCS.NS.csv")

plt.plot(df["Close"])
plt.title("TCS Closing Price")
plt.show()