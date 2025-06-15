import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from utils.plotting import custom_ncmap

# データ読み込み
df = pd.read_csv('data_2Dmap_8Org_Broth.csv')

# UI構築
st.title('pH vs aw Scatter Plot')
st.write('Select conditions to visualize predicted growth (log(Nt/N0) change)')

# Organism, Category, Name 選択
organisms = sorted(df['Organism'].unique())
organism = st.selectbox('Organism', organisms)

categories = sorted(df[df['Organism'] == organism]['Category'].unique())
category = st.selectbox('Category', categories)

names = sorted(df[(df['Organism'] == organism) & (df['Category'] == category)]['Name'].unique())
name = st.selectbox('Name', names)

# 温度スライダー（データの最小～最大でも良い場合は変更可）
temp_min, temp_max = int(df['Temperature'].min()), int(df['Temperature'].max())
temperature = st.slider('Temperature (°C)', min_value=0, max_value=25, value=20)

# データ抽出
d0 = df[
    (df['Organism'] == organism) &
    (df['Category'] == category) &
    (df['Name'] == name) &
    (df['Temperature'] == temperature)
]

if d0.empty:
    st.warning('No data for this condition.')
    st.stop()

# データ分割
d_0 = d0[(d0['Predict'] >= -1.0) & (d0['Predict'] < 1.0)]
d_n1 = d0[(d0['Predict'] >= -3.0) & (d0['Predict'] < -1.0)]
d_p1 = d0[(d0['Predict'] >= 1.0) & (d0['Predict'] < 3.0)]
d_n2 = d0[d0['Predict'] < -3.0]
d_p2 = d0[d0['Predict'] >= 3.0]


cmap = custom_ncmap('coolwarm', 5)

# プロット
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(3.2, 7.8)
ax.set_ylim(0.894, 0.996)
ax.set_xticks([3.5, 5.5, 7.5])
ax.set_yticks([0.90, 0.945, 0.99])
ax.tick_params(axis='both', labelsize=15)
ax.set_xlabel('pH', fontsize=18)
ax.set_ylabel('$a_{w}$', fontsize=18)
ax.set_title(f'{organism}\n{name} | {category} | {temperature}℃', fontsize=20, fontstyle='italic')

ax.scatter(d_p2['pH'], d_p2['Aw'], marker='s', color=cmap[4], s=200, label='≥ 3 log(Nt/N0)')
ax.scatter(d_p1['pH'], d_p1['Aw'], marker='s', color=cmap[3], s=200, label='1-3 log(Nt/N0)')
ax.scatter(d_0['pH'], d_0['Aw'], marker='s', color=cmap[2], s=200, label='-1～1 log(Nt/N0)')
ax.scatter(d_n1['pH'], d_n1['Aw'], marker='s', color=cmap[1], s=200, label='-1～-3 log(Nt/N0)')
ax.scatter(d_n2['pH'], d_n2['Aw'], marker='s', color=cmap[0], s=200, label='< -3 log(Nt/N0)')

ax.legend(loc='best', fontsize=12, title='Change Ratio')
st.pyplot(fig)
