import pandas as pd
stop_words = pd.read_csv("stop_words.csv", delimiter=",", encoding='cp949')
print(stop_words) 
