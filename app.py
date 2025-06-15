import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.plotting import custom_ncmap

# データ読み込み
df = pd.read_csv('data_2Dmap_8Org_Broth.csv')

st.title('2D Growth Map Viewer')
st.write('Select axes and conditions to visualize predicted growth (log(Nt/N0) change)')

# 軸の選択
axes_options = {
    "pH × aw": ("pH", "Aw", "Temperature"),
    "pH × Temperature": ("pH", "Temperature", "Aw"),
    "Temperature × aw": ("Temperature", "Aw", "pH"),
}
axis_key = st.selectbox('Plot Axes', list(axes_options.keys()))
x_col, y_col, fixed_col = axes_options[axis_key]

# Organism, Category, Name 選択
organisms = sorted(df['Organism'].unique())
organism = st.selectbox('Organism', organisms)

categories = sorted(df[df['Organism'] == organism]['Category'].unique())
category = st.selectbox('Category', categories)

names = sorted(df[(df['Organism'] == organism) & (df['Category'] == category)]['Name'].unique())
name = st.selectbox('Name', names)

# 固定軸の値選択（実データの値を自動抽出＆整数/小数スライダー自動化）
vals = sorted(df[fixed_col].dropna().unique())
# 連続値ならslider, カテゴリ値ならselectbox
if len(vals) > 15 and df[fixed_col].dtype != object:
    val = st.slider(f'{fixed_col}', float(min(vals)), float(max(vals)), float(vals[0]))
else:
    val = st.selectbox(f'{fixed_col}', vals)

# データ抽出
query = (
    (df['Organism'] == organism) &
    (df['Category'] == category) &
    (df['Name'] == name) &
    (df[fixed_col] == val)
)
d0 = df[query]

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

# 軸設定ごとの範囲・ラベル
xlim_dict = {
    "pH": (3.2, 7.8), "Aw": (0.894, 0.996), "Temperature": (0, 25)
}
xticks_dict = {
    "pH": [3.5, 5.5, 7.5], "Aw": [0.90, 0.945, 0.99], "Temperature": [0, 12.5, 25]
}
xlabel_dict = {"pH": "pH", "Aw": "$a_{w}$", "Temperature": "Temperature [°C]"}

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(*xlim_dict[x_col])
ax.set_ylim(*xlim_dict[y_col])
ax.set_xticks(xticks_dict[x_col])
ax.set_yticks(xticks_dict[y_col])
ax.set_xlabel(xlabel_dict[x_col], fontsize=18)
ax.set_ylabel(xlabel_dict[y_col], fontsize=18)

# Organismだけイタリック
organism_latex = r"$\it{" + organism.replace(' ', r'\ ') + "}$"
title_str = f'{organism_latex}\n({category} - {name}, {fixed_col}={val})'
ax.set_title(title_str, fontsize=20)

# プロット
def scatter_subgroup(df, color, label):
    ax.scatter(df[x_col], df[y_col], marker='s', color=color, s=400, label=label)

scatter_subgroup(d_p2, cmap[4], '≥ 3 log(Nt/N0)')
scatter_subgroup(d_p1, cmap[3], '1-3 log(Nt/N0)')
scatter_subgroup(d_0, cmap[2], '-1～1 log(Nt/N0)')
scatter_subgroup(d_n1, cmap[1], '-1～-3 log(Nt/N0)')
scatter_subgroup(d_n2, cmap[0], '< -3 log(Nt/N0)')

ax.legend(loc='best', fontsize=12, title='Change Ratio')
st.pyplot(fig)
